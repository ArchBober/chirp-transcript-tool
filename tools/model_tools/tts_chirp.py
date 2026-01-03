from google.cloud import texttospeech, storage

import time
import io
import gc
import asyncio

from typing import Tuple, Dict, List

from config import TTS_VOICE, LANGUAGE, SPEAKING_RATE, TTS_CHIRP_TOKEN_PRICE

async def tts_chirp(input_content: Dict[str, str], bucket_name: str, credentials, preserve_file_in_bucket = True, cost_single: bool = False, verbose: bool = False) -> List[str]:
    # try:
    save_dir: str = "samples/temp"
    if verbose:
        overall_tokens = 0.
        overall_tokens_price = 0.
        print(f"Setting TTS client with model and storage client (Chirp - {TTS_VOICE}) and sending request.")

    # for key, val in input_content.items():
    coros = [_get_audio(key, val, credentials, save_dir, bucket_name, preserve_file_in_bucket, cost_single, verbose) for key, val in input_content.items()]


    results = await asyncio.gather(*coros)

    filepaths, overall_tokens, overall_tokens_price = map(list, zip(*results))
        
    if verbose:
        print("\n===OVERALL COST===")
        print(f"Tokens: {sum(overall_tokens)} --- Cost: {sum(overall_tokens_price):.6f} $")
        print("===$$$===\n")

    # except Exception as e:
    #     print(f"\nError: {e}")
    
    return filepaths

def _estimate_tts_price(text: str) -> (str, str):
    tokens =  len(text)
    tokens_price = tokens / 1_000_000 * TTS_CHIRP_TOKEN_PRICE

    return tokens, tokens_price

def _tts_configuration_init():
    voice = texttospeech.VoiceSelectionParams(
            language_code=LANGUAGE,
            name=f"{LANGUAGE}-Chirp3-HD-" + TTS_VOICE,
        )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16,
        speaking_rate=SPEAKING_RATE
    )
    return voice, audio_config

def _get_audio_filename(filename: str) -> str:
    filename_split = filename.split('.')
    if len(filename_split) > 2:
        raise Exception("multiple dots in text file")
    return filename_split[0] + "_" + time.strftime("%Y%m%d_%H%M%S") + ".wav"


async def _get_audio(
    filename: str, 
    transcript: str, 
    credentials,
    save_dir: str,
    bucket_name, 
    preserve_file_in_bucket,
    cost_single: bool,
    verbose: bool
):
    tokens = 0.
    tokens_price = 0.
    client_tts = texttospeech.TextToSpeechLongAudioSynthesizeAsyncClient(
        credentials=credentials
    )

    filepaths = []

    voice, audio_config = _tts_configuration_init()

    storage_client = storage.Client(credentials=credentials)

    bucket = storage_client.bucket(bucket_name)

    synthesis_input = texttospeech.SynthesisInput(
        text=transcript,
    )

    file_name = _get_audio_filename(filename)
    save_filepath = save_dir + '/' + file_name
    output_gcs_uri = f'gs://{bucket_name}/{save_dir}/{file_name}'

    request = texttospeech.SynthesizeLongAudioRequest(
        parent=f"projects/{credentials.project_id}/locations/us-central1",
        input=synthesis_input,
        audio_config=audio_config,
        voice=voice,
        output_gcs_uri=output_gcs_uri,
    )

    if verbose:
        print(f"Requesting Audio content to bucket: {output_gcs_uri}")

    operation = await client_tts.synthesize_long_audio(request=request)

    await operation.result(timeout=600)

    if verbose:
        print(f"Audio synthesized to GCS. Downloading: {output_gcs_uri}")

    def download_and_cleanup():
        storage_client = storage.Client(credentials=credentials)
        bucket = storage_client.bucket(bucket_name)
        blob_name = f"{save_dir}/{file_name}"
        blob = bucket.blob(blob_name)
        
        blob.download_to_filename(save_filepath)
        
        if not preserve_file_in_bucket:
            blob.delete()
            if verbose:
                print(f"Blob deleted: {blob_name}")
        
    await asyncio.to_thread(download_and_cleanup)

    gc.collect()

    if verbose:
        print(f"Finished: {file_name}")
        tokens, tokens_price = _estimate_tts_price(transcript)
        if cost_single:
            print("===COST===")
            print(f"Tokens: {tokens} --- Cost: {tokens_price:.6f} $")
            print("===$$$===")

    return save_filepath, tokens, tokens_price


