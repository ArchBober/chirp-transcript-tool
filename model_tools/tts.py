# from google.cloud import texttospeech

# from pydub import AudioSegment
# import io

# from config import TTS_MODEL, TTS_PROMPT, TTS_VOICE, LANGUAGE, SPEAKING_RATE, TTS_AUDIO_TOKEN_PRICE, TTS_TEXT_TOKEN_PRICE

# def tts(client_tts: texttospeech.TextToSpeechClient, input_content: str, save_filepath: str = "sample_output.mp3", verbose: bool = False) -> None:
#     try:
#         if verbose:
#             print(f"Setting TTS client with model ({TTS_MODEL} - {TTS_VOICE}) and sending request.")

#         synthesis_input = texttospeech.SynthesisInput(
#             text=input_content, 
#             prompt=TTS_PROMPT
#         )
        
#         voice = texttospeech.VoiceSelectionParams(
#             language_code=LANGUAGE,
#             name=TTS_VOICE,
#             model_name=TTS_MODEL
#         )

#         audio_config = texttospeech.AudioConfig(
#             audio_encoding=texttospeech.AudioEncoding.MP3,
#             speaking_rate=SPEAKING_RATE
#         )

#         response = client_tts.synthesize_speech(
#             input=synthesis_input, voice=voice, audio_config=audio_config
#         )

#         if verbose:
#             print("Got response, saving it to file")
#             text_tokens, text_tokens_price, audio_tokens, audio_tokens_price = estimate_tts_price(input_content, TTS_PROMPT, response.audio_content)
#             print("\n===COST===")
#             print(f"Text tokens: {text_tokens} --- Cost: {text_tokens_price:.6f} $")
#             print(f"Audio tokens: {audio_tokens} --- Cost: {audio_tokens_price:.6f} $")
#             print("===$$$===\n")

#         with open(save_filepath, "wb") as out:
#             out.write(response.audio_content)
#             print(f"Audio content written to file: {save_filepath}")
    
#     except Exception as e:
#         print(f"\nError: {e}")
    
#     return

# def estimate_tts_price(text: str, prompt: str, audio_content: bytes):
#     audio = AudioSegment.from_file(io.BytesIO(audio_content))
#     seconds = len(audio) / 1000.0

#     audio_tokens = int(seconds * 25)
#     audio_tokens_price = audio_tokens / 1_000_000 * TTS_AUDIO_TOKEN_PRICE

#     text_tokens =  len(text) + len(prompt)
#     text_tokens_price = text_tokens / 1_000_000 * TTS_TEXT_TOKEN_PRICE

#     return text_tokens, text_tokens_price, audio_tokens, audio_tokens_price