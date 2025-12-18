import whisperx
import whisper
import torch
import os

def stt_timestamps(audio_path, verbose: bool = False):
    """
    Takes an audio path, generates word-level timestamps using WhisperX.
    """

    # test_whisper(audio_path[0], verbose)
    os.environ["TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD"] = 'true'
    
    device = "cuda"
    batch_size = 16 
    compute_type = "float16" if device == "cuda" else "int8"
    
    if verbose:
        print(f"Loading WhisperX on {device}, batch_size = {batch_size}, compute_type = {compute_type}")

    model = whisperx.load_model("large-v2", device, compute_type=compute_type)

    for filepath in audio_path:
        audio = whisperx.load_audio(filepath)
        result = model.transcribe(audio, batch_size=batch_size)
        
        if verbose:
            print("Cleaning memory")

        del model
        torch.cuda.empty_cache()

        if verbose:
            print("Generating timestamps...")

        model_a, metadata = whisperx.load_align_model(language_code='en', device=device)
        
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
    
    return word_timestamps

def test_whisper(audio_filepath: str, verbose: bool = False) -> str:
    if verbose:
        print("Initializing STT client (Whisper)")
    # ctrl+c ctrl+v from wshiper readme but work perfectly
    stt_model = whisper.load_model("turbo")

    if verbose:
        print(f"Loading audio from '{audio_filepath}' and finding language")
    # load audio and pad/trim it to fit 30 seconds
    audio = whisper.load_audio(audio_filepath)
    audio = whisper.pad_or_trim(audio)

    # make log-Mel spectrogram and move to the same device as the model
    mel = whisper.log_mel_spectrogram(audio, n_mels=stt_model.dims.n_mels).to(stt_model.device)

    # detect the spoken language
    # TODO add loop if lang != EN or enforce EN transciption
    _, probs = stt_model.detect_language(mel)
    if verbose:
        print(f"Detected language: {max(probs, key=probs.get)}")
        print("Decoding Audio")

    # decode the audio
    options = whisper.DecodingOptions()
    result_audio_trans = whisper.decode(stt_model, mel, options)

    del stt_model

    # print the recognized text
    if verbose:
        print("\n---Audio Transcript---")
        print(result_audio_trans.text)
        print("------------\n")

    return result_audio_trans.text

if __name__ == "__main__":
    # Your file in the project directory
    my_audio_file = "chirp_output.wav" 
    
    try:
        timestamps = get_timestamps(my_audio_file)
        
        # Print the first 5 words as a test
        print("\nSuccess! Here are the first 5 words:")
        for t in timestamps[:5]:
            print(f"{t['start']:.2f} - {t['end']:.2f}: {t['word']}")
            
    except Exception as e:
        print(f"Error: {e}")
