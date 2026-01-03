import whisperx
import whisper
import torch
import gc

import os
import contextlib
import sys
import warnings
import logging

from config import SRT_MAX_GAP, SRT_MAX_CHARS

# temp solution for 1000 warnings from whisper
@contextlib.contextmanager
def no_print():
    # Open the null device (a black hole for data)
    with open(os.devnull, "w") as devnull:
        # 1. Get the file descriptors for stdout (1) and stderr (2)
        old_stdout = sys.stdout.fileno()
        old_stderr = sys.stderr.fileno()

        # 2. Duplicate the original FDs so we can restore them later
        saved_stdout = os.dup(old_stdout)
        saved_stderr = os.dup(old_stderr)

        # 3. Flush Python buffers to ensure no queued text gets printed
        sys.stdout.flush()
        sys.stderr.flush()

        try:
            # 4. Redirect stdout and stderr to devnull at the OS level
            os.dup2(devnull.fileno(), old_stdout)
            os.dup2(devnull.fileno(), old_stderr)
            yield
        finally:
            # 5. Restore the original file descriptors
            os.dup2(saved_stdout, old_stdout)
            os.dup2(saved_stderr, old_stderr)
            
            # 6. Clean up the duplicated FDs
            os.close(saved_stdout)
            os.close(saved_stderr)

def stt_timestamps(audio_path, verbose: bool = False, srt_timestamps: bool = True):
    """
    Takes an audio path, generates word-level timestamps using WhisperX.
    """

    # some magic errors from whisperx prevent from loading models
    os.environ["TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD"] = 'true'
    
    device = "cuda"
    batch_size = 8
    compute_type = "float16" if device == "cuda" else "int8"
    
    if verbose:
        print(f"Loading WhisperX on {device}, batch_size = {batch_size}, compute_type = {compute_type}")

    with no_print():
        model = whisperx.load_model("large-v2", device, compute_type=compute_type)

    if verbose:
        print("Loading allign model")

    with no_print():
        model_a, metadata = whisperx.load_align_model(language_code='en', device=device)


    for filepath in audio_path:
        try:
            if verbose:
                print("Transcribing audio")

            with no_print():
                audio = whisperx.load_audio(filepath)
                result = model.transcribe(audio, batch_size=batch_size)

            if verbose:
                print("Cleaning memory - transcribe")


            torch.cuda.empty_cache()

            if verbose:
                print("Generating timestamps")

            
            aligned_result = whisperx.align(
                result["segments"], 
                model_a, 
                metadata, 
                audio, 
                device, 
                return_char_alignments=False
            )

            word_timestamps = []
        
            for segment in aligned_result["segments"]:
                for word in segment["words"]:
                    if "start" in word:
                        word_timestamps.append({
                            "word": word["word"],
                            "start": word["start"],
                            "end": word["end"]
                        })

            if verbose:
                print(f"Timestamps for file {filepath} generated.")

            if srt_timestamps:
                if verbose:
                    print("Generating SRT timestamps")

                word_timestamps = _timestamps_to_srt(word_timestamps, SRT_MAX_CHARS, SRT_MAX_GAP) # later ill refactror

            filename = _get_transcript_filename(filepath.split('/')[-1])
            _save_transcript(word_timestamps, filename)

            if verbose:
                print(f"Transcribing done file saved to {filename}")

        except Exception as e:
            print(f"Error processing {filepath}: {e}")

        finally:
            if verbose:
                print("Cleaning")

            if 'audio' in locals(): del audio
            if 'result' in locals(): del result
            if 'aligned_result' in locals(): del aligned_result
            
            # 2. Force Python Garbage Collector
            gc.collect()
            
            # 3. Force PyTorch to empty the CUDA cache
            torch.cuda.empty_cache()

    return word_timestamps

def _save_transcript(text: str, name: str = "output.txt", text_format: str = 'srt'):
    with open(f"timestamped_transcriptions/{name}.{text_format}", "w", encoding="utf-8") as f:
        f.write(str(text))


def _get_transcript_filename(filename: str) -> str:
    filename_split = filename.split('.')
    if len(filename_split) > 2:
        raise Exception("multiple dots in text file")
    return filename_split[0] + ".txt"

def _timestamps_to_srt(word_list, max_chars=40, max_gap=2.0):
    """
    Converts a list of word dictionaries (with start/end timestamps) into SRT format.
    
    Args:
        word_list (list): List of dicts e.g., [{'word': 'Hello', 'start': 0.5, 'end': 0.9}, ...]
        max_chars (int): Maximum characters per subtitle line before splitting.
        max_gap (float): Maximum gap (seconds) between words before forcing a new line.
    
    Returns:
        str: The complete SRT formatted string.
    """
    
    def format_time(seconds):
        """Helper to convert seconds to HH:MM:SS,mmm format"""
        seconds = float(seconds) # Ensure it's a standard float (not numpy)
        millis = int((seconds % 1) * 1000)
        seconds = int(seconds)
        minutes = seconds // 60
        hours = minutes // 60
        minutes %= 60
        seconds %= 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d},{millis:03d}"

    srt_output = []
    
    if not word_list:
        return ""

    # Initialize variables for grouping
    current_segment = []
    segment_start = 0.
    current_length = 0
    idx = 1

    sentence_endings = {'.', '!', '?'}
    
    for i, item in enumerate(word_list):
        word = item['word']
        start = float(item['start'])
        end = float(item['end'])
        
        # Calculate gap from previous word (if not first word)
        time_gap = 0
        if i > 0:
            prev_end = float(word_list[i-1]['end'])
            time_gap = start - prev_end
            
        
        # DECISION: Start a new subtitle block?
        # 1. If adding this word exceeds max characters
        # 2. OR if there is a long silence (max_gap) before this word
        if (current_length + len(word) + 1 > max_chars) or (time_gap > max_gap):
            if current_segment:
                # Finalize the previous segment
                segment_end = float(word_list[i-1]['end'])
                text = " ".join(current_segment)
                srt_output.append(f"{idx}\n{format_time(segment_start)} --> {format_time(segment_end)}\n{text}\n")
                idx += 1
            
            # Reset for new segment
            current_segment = []
            segment_start = start
            current_length = 0

        current_segment.append(word)
        current_length += len(word) + 1 # +1 for the space

        # DECISION: Force a NEW line AFTER adding this word?
        # Check if this word ends with punctuation (., !, ?)
        if word and word[-1] in sentence_endings:
            segment_end = end
            text = " ".join(current_segment)
            srt_output.append(f"{idx}\n{format_time(segment_start)} --> {format_time(segment_end)}\n{text}\n")
            idx += 1
            
            # Reset
            current_segment = []
            segment_start = start
            current_length = 0

    # Flush the last remaining segment
    if current_segment:
        segment_end = float(word_list[-1]['end'])
        text = " ".join(current_segment)
        srt_output.append(f"{idx}\n{format_time(segment_start)} --> {format_time(segment_end)}\n{text}\n")

    return "\n".join(srt_output)
