from google.cloud import texttospeech, storage
import time

import io

from typing import Tuple, Dict, List

from config import TTS_VOICE, LANGUAGE, SPEAKING_RATE, TTS_CHIRP_TOKEN_PRICE

def tts_chirp(client_tts: texttospeech.TextToSpeechClient, input_content: Dict[str, str], bucket_name: str, credentials, save_dir: str = "response_audio", preserve_file_in_bucket = True, verbose: bool = False) -> List[str]:
    try:
        if verbose:
            overall_tokens - 0.
            overall_tokens_price = 0.
            print(f"Setting TTS client with model (Chirp - {TTS_VOICE}) and sending request.")

        filepaths = []

        voice, audio_config = _tts_configuration_init()

        for key, val in input_content.items():
            synthesis_input = texttospeech.SynthesisInput(
                text=val,
            )

            file_name = _get_audio_filename(key)
            save_filepath = save_dir + '/' + file_name

            request = texttospeech.SynthesizeLongAudioRequest(
                parent=f"projects/ia-agent-474100/locations/us-central1",
                input=synthesis_input,
                audio_config=audio_config,
                voice=voice,
                output_gcs_uri=f'gs://{bucket_name}/chirp_long_audio/{file_name}',
            )

            if verbose:
                print(f"Requesting Audio content to bucket: {bucket_name}")

            operation = client_tts.synthesize_long_audio(request=request)

            result = operation.result(timeout=300)

            if verbose:
                print(f"Downloading audio from bucket: {bucket_name}/chirp_long_audio/{file_name}")

            storage_client = storage.Client(credentials=credentials)

            bucket = storage_client.bucket(bucket_name)

            blob = bucket.blob(f"chirp_long_audio/{file_name}")
            blob.download_to_filename(save_filepath)

            filepaths.append(save_filepath)

            if verbose:
                print(f"Audio content written to file: {file_name}")
                tokens, tokens_price = _estimate_tts_price(input_content)

                overall_tokens += tokens
                overall_tokens_price += tokens_price

                print("\n===COST===")
                print(f"Tokens: {text_tokens} --- Cost: {text_tokens_price:.6f} $")
                print("===$$$===\n")

        if verbose:
            print("\n===OVERALL COST===")
            print(f"Tokens: {overall_tokens} --- Cost: {overall_tokens_price:.6f} $")
            print("===$$$===\n")
    
    except Exception as e:
        print(f"\nError: {e}")
    
    return filepaths

def _estimate_tts_price(text: str) -> (str, str):
    tokens =  len(text)
    tokens_price = tokens / 1_000_000 * TTS_CHIRP_TOKEN_PRICE

    return tokens, tokens_price

def _tts_configuration_init():
    voice = texttospeech.VoiceSelectionParams(
            language_code=LANGUAGE,
            name="en-US-Chirp3-HD-" + TTS_VOICE,
        )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16,
        speaking_rate=SPEAKING_RATE
    )
    return voice, audio_config

def _get_audio_filename(filename: str) -> str:
    filename_split = filename.split('.')
    if filename_split > 2:
        raise Exception("multiple dots in text file")
    return filename_split[0] , "_" + time.strftime("%Y%m%d_%H%M%S") + ".wav"

def _deletye_from_bucket(filename: str):
    return None
