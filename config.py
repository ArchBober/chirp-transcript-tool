from prompt_chirp_doc import prompt_chirp_doc

TTS_TEXT_FILE = 'tts_input_long.txt'

SPEAKING_RATE = 1.1 # 1 is default - use range 0.5-2.0

LLM_MODEL = "gemini-3-pro-preview"
TTS_VOICE = "Sadaltager"


LLM_CHIRP_PROMPT = f"""
Your job is to generate based on this documentation transcript for natural voice that will be added for CHIRP model for generating speech (TTS). DO NOT CHANGE ANY TEXT. 
You can only add elements that are described in documentation for more natural human voice. 
Only respond with updated text that you get and nothing more. 
Try not to add many pauses (or even none) so conversation is straight forward.\n
""" + prompt_chirp_doc

LLM_INPUT_TOKEN_PRICE = 4.
LLM_OUTPUT_TOKEN_PRICE = 8.

TTS_TEXT_TOKEN_PRICE = 30.

# To del propably
TTS_MODEL = "en-US-Chirp3-HD-Charon"
STT_MODEL = "turbo" # tiny, base 1GB / small 2GB / medium 5GB / large 10 GB / turbo 6GB (VRAM)

TTS_PROMPT=f""""""