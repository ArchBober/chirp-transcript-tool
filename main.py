from google.oauth2 import service_account
from google import genai
from google.cloud import texttospeech

from dotenv import load_dotenv
import subprocess, shlex
import sys
import os

from model_tools.stt import stt
from model_tools.llm import llm
from model_tools.tts_chirp import tts_chirp

from tools.flags_parser import parse_flags
from tools.read_transcripts import read_transcripts

from config import OUTPUT_AUDIO_FILEPATH, TTS_TEXT_FILE, LLM_PROMPT, LLM_CHIRP_PROMPT
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

    if verbose:
        print("Initializing TTS client")

    client_tts = texttospeech.TextToSpeechLongAudioSynthesizeClient(
        credentials=credentials
    )

    flags, args = parse_flags()

    if flags["prompt"]:
        transcripts['prompt.txt'] = args.copy()
    else:
        path = args[0] if flags["from_file"] or flags["from_dir"] else TTS_TEXT_FILE

        transcripts = read_transcripts()
    


    if not flags["no_tuning"]:
        if verbose:
            print("Initializing LLM client")

        client_llm = genai.Client(
            vertexai=True, api_key=api_key
        )

        llm_responses = llm(client_llm, transcripts, verbose, LLM_CHIRP_PROMPT)
    else:
        llm_responses = transcripts.copy()


    filepath = tts_chirp(client_tts, llm_response, bucket_name, credentials, OUTPUT_AUDIO_FILEPATH, verbose)

    if verbose:
        print("Running ffmpeg remove silence")

    file_out = "tr_" + filepath

    subprocess.run(
        shlex.split(f'ffmpeg -y -i {filepath} -af silenceremove=stop_periods=-1:stop_duration=0.1:stop_threshold=-30dB {file_out}'),
        stdout=subprocess.DEVNULL,
        check=True)
    
    if verbose:
        print(f"Done cut silence. File saved to trunc_{filepath}")







if __name__ == "__main__":
    main()