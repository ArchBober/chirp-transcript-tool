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

   


    llm_response = ""

    try:
        with open(TTS_TEXT_FILE, 'r', encoding='utf-8') as f:
            transcription = f.read()
            if verbose:
                print(f"Text file opened and read: {TTS_TEXT_FILE}")

        if not no_tuning:
            if verbose:
                print("Initializing LLM client")

            client_llm = genai.Client(
                vertexai=True, api_key=api_key
            )

            llm_response = llm(client_llm, transcription, verbose, LLM_CHIRP_PROMPT)

        if verbose:
            print("Initializing TTS client")

        client_tts = texttospeech.TextToSpeechLongAudioSynthesizeClient(
            credentials=credentials
        )

        if not llm_response:
            llm_response = transcription

        filepath = tts_chirp(client_tts, llm_response, bucket_name, credentials, OUTPUT_AUDIO_FILEPATH, verbose)

        if verbose:
            print("Running cut silence")

        file_out = "tr_" + filepath

        subprocess.run(
            shlex.split(f'ffmpeg -y -i {filepath} -af silenceremove=stop_periods=-1:stop_duration=0.1:stop_threshold=-30dB {file_out}'),
            stdout=subprocess.DEVNULL,
            check=True)
        
        if verbose:
            print(f"Done cut silence. File saved to trunc_{filepath}")

    except FileNotFoundError:
        print(f"The file '{file_path}' was not found. Check the path and try again.")
    except IOError as e:
        print(f"An I/O error occurred: {e}")






if __name__ == "__main__":
    main()