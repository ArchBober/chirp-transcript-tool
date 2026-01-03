from descriptions.prompt_chirp_doc import prompt_chirp_doc

TTS_TEXT_FILE = 'transcriptions/tts_default.txt'

OUTPUT_AUDIO_DIR = "response_audio"
EDITED_AUDIO_DIR = "edited_audio"

SPEAKING_RATE = 1.1 # 1 is default - use range 0.5-2.0
TTS_VOICE = "Sadaltager"
LANGUAGE="en-US"

LLM_MODEL = "gemini-3-pro-preview"


LLM_CHIRP_PROMPT = f"""
Your job is to generate based on this documentation transcript for natural voice that will be added for CHIRP model for generating speech (TTS). DO NOT CHANGE ANY TEXT. 
You can only add elements that are described in documentation for more natural human voice. 
Only respond with updated text that you get and nothing more. 
Try not to add many pauses (or even none) so conversation is straight forward.\n
""" + prompt_chirp_doc

LLM_INPUT_TOKEN_PRICE = 4.
LLM_OUTPUT_TOKEN_PRICE = 8.

TTS_CHIRP_TOKEN_PRICE = 30.


SRT_MAX_CHARS = 70
SRT_MAX_GAP = 2.0 # in seconds