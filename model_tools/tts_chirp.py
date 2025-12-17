from google.cloud import texttospeech, storage
import time

from pydub import AudioSegment
import io

from config import TTS_MODEL, TTS_PROMPT, TTS_VOICE, LANGUAGE, SPEAKING_RATE, TTS_AUDIO_TOKEN_PRICE, TTS_TEXT_TOKEN_PRICE

def tts_chirp(client_tts: texttospeech.TextToSpeechClient, input_content: str, bucket_name: str, credentials, save_filepath: str = "sample_output.mp3", verbose: bool = False) -> None:
    try:
        if verbose:
            print(f"Setting TTS client with model (Chirp - {TTS_VOICE}) and sending request.")

        
        synthesis_input = texttospeech.SynthesisInput(
            text=input_content, 
            # prompt=TTS_PROMPT
        )
        # print(synthesis_input)
        voice = texttospeech.VoiceSelectionParams(
            language_code=LANGUAGE,
            name="en-US-Chirp3-HD-" + TTS_VOICE,
            # model_name=TTS_MODEL
        )

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16,
            speaking_rate=SPEAKING_RATE
        )

        # response = client_tts.synthesize_speech(
        #     input=synthesis_input, voice=voice, audio_config=audio_config
        # )

        ts = "response_" + time.strftime("%Y%m%d_%H%M%S") + ".wav"

        request = texttospeech.SynthesizeLongAudioRequest(
            parent=f"projects/ia-agent-474100/locations/us-central1",
            input=synthesis_input,
            audio_config=audio_config,
            voice=voice,
            output_gcs_uri=f'gs://{bucket_name}/chirp_long_audio/{ts}',

        )

        if verbose:
            print(f"Requesting Audio content to bucket: {bucket_name}")

        operation = client_tts.synthesize_long_audio(request=request)

        result = operation.result(timeout=300)

        if verbose:
            print(f"Downloading audio from bucket: {bucket_name}/chirp_long_audio/{ts}")

        storage_client = storage.Client(credentials=credentials)

        bucket = storage_client.bucket(bucket_name)

        blob = bucket.blob(f"chirp_long_audio/{ts}")
        blob.download_to_filename(ts)

        if verbose:
            print(f"Audio content written to file: {ts}")

            text_tokens, text_tokens_price, audio_tokens, audio_tokens_price = estimate_tts_price(input_content, "")
            print("\n===COST===")
            print(f"Text tokens: {text_tokens} --- Cost: {text_tokens_price:.6f} $")
            print(f"Audio tokens: {audio_tokens} --- Cost: {audio_tokens_price:.6f} $")
            print("===$$$===\n")
    
    except Exception as e:
        print(f"\nError: {e}")
    
    return ts

def estimate_tts_price(text: str, prompt: str):
    audio_tokens_price = 0.
    audio_tokens = 0.

    text_tokens =  len(text) + len(prompt)
    text_tokens_price = text_tokens / 1_000_000 * TTS_TEXT_TOKEN_PRICE

    return text_tokens, text_tokens_price, audio_tokens, audio_tokens_price