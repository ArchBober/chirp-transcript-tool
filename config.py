from prompt_chirp_doc import prompt_chirp_doc

OUTPUT_AUDIO_FILEPATH = "response.wav"

LANGUAGE="en-US"
LANGUAGE_LVL = "B1"
SPEAKING_RATE = 1.1 # 1 is default - use range 0.5-2.0

STT_MODEL = "turbo" # tiny, base 1GB / small 2GB / medium 5GB / large 10 GB / turbo 6GB (VRAM)
LLM_MODEL = "gemini-3-pro-preview"
TTS_MODEL = "en-US-Chirp3-HD-Charon"
TTS_VOICE = "Sadaltager"

LLM_PROMPT = f"""
You are {LANGUAGE} teacher that help with basic difficulties of learning that language.
Your main goal is to talk to student and use not too many hard words.
Students are expected to be on level A1 up to B2 in that language. 
Your today student is expected to be on {LANGUAGE_LVL} language profficiency.
Your name is Mark Spencer but tell your name only when asked. Also try to keep responses short and straight to the point. 
If possible try to end sentences with questions for student to keep conversation.
"""
TTS_PROMPT=f"""As a teacher of {LANGUAGE} language talk with calm and polite voice."""

MAX_CHARS = 10000

LLM_INPUT_TOKEN_PRICE = 4.
LLM_OUTPUT_TOKEN_PRICE = 8.

TTS_AUDIO_TOKEN_PRICE = 30.
TTS_TEXT_TOKEN_PRICE = 30.


TTS_TEXT_FILE = 'tts_input_long.txt'

LLM_CHIRP_PROMPT = f"""
Your job is to generate based on this documentation transcript for natural voice that will be added for CHIRP model for generating speech (TTS). DO NOT CHANGE ANY TEXT. 
You can only add elements that are described in documentation for more natural human voice. 
Only respond with updated text that you get and nothing more. 
Try not to add many pauses (or even none) so conversation is straight forward.\n
""" + prompt_chirp_doc