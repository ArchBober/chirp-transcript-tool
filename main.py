from google.oauth2 import service_account
from google import genai
from google.cloud import texttospeech

from dotenv import load_dotenv
import os

from model_tools.llm import llm
from model_tools.tts_chirp import tts_chirp

from tools.flags_parser import parse_flags
from tools.read_transcripts import read_transcripts
from tools.ffmpeg_cutter import cut_silence

from config import TTS_TEXT_FILE, LLM_CHIRP_PROMPT, OUTPUT_AUDIO_DIR, EDITED_AUDIO_DIR
from descriptions.help_description import HELP_DESCRIPTION

import warnings

def main():
    load_dotenv()

    api_key = os.environ.get("VERTEX_AI_API_KEY")
    secret_json_filepath = os.environ.get("SECRET_JSON_FILEPATH")
    bucket_name = os.environ.get("BUCKET_NAME")

    credentials=service_account.Credentials.from_service_account_file(
        secret_json_filepath
    )

    flags, args = parse_flags()
    
    if flags["verbose"]:
        print("Initializing TTS client")

    client_tts = texttospeech.TextToSpeechLongAudioSynthesizeClient(
        credentials=credentials
    )

    if flags["prompt"]:
        transcripts['prompt.txt'] = args.copy()
    else:
        path = args[0] if flags["from_file"] or flags["from_dir"] else TTS_TEXT_FILE

        transcripts = read_transcripts(path, flags["from_dir"])
    

    if not flags["no_tuning"]:
        if flags["verbose"]:
            print("Initializing LLM client")

        client_llm = genai.Client(
            vertexai=True, api_key=api_key
        )

        llm_responses = llm(client_llm, transcripts, flags["verbose"], LLM_CHIRP_PROMPT)
    else:
        llm_responses = transcripts.copy()


    # filepaths = tts_chirp(client_tts, llm_responses, bucket_name, credentials, OUTPUT_AUDIO_DIR, flags["--no-bucket-preserve"], flags["verbose"])


    # cut_silence(filepaths, EDITED_AUDIO_DIR, flags['verbose'])
    

if __name__ == "__main__":
    main()