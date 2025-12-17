from google.oauth2 import service_account
from google import genai
from google.cloud import texttospeech

import subprocess, shlex
import sys
import os

from stt import stt
from llm import llm
from tts import tts
from tts_chirp import tts_chirp
from config import OUTPUT_AUDIO_FILEPATH, TTS_TEXT_FILE, LLM_PROMPT, LLM_CHIRP_PROMPT
from help_description import HELP_DESCRIPTION

from dotenv import load_dotenv

import warnings

# ignore regex warning from pydub
warnings.filterwarnings(
    action="ignore",      
    category=UserWarning,          
    module=r"^pydub\.",           
    message=r".*"                 
)

def main():
    load_dotenv()

    api_key = os.environ.get("VERTEX_AI_API_KEY")
    secret_json_filepath = os.environ.get("SECRET_JSON_FILEPATH")
    bucket_name = os.environ.get("BUCKET_NAME")

    credentials=service_account.Credentials.from_service_account_file(
        secret_json_filepath
    )

    if "--help" in sys.argv:
        print(HELP_DESCRIPTION)
        sys.exit(0)

    verbose = "--verbose" in sys.argv
    prompt = "--prompt" in sys.argv
    chirp_flag = "--chirp" in sys.argv
    no_tuning = "--no-tuning" in sys.argv

    args = []
    for arg in sys.argv[1:]:
        if not arg.startswith("--"):
            args.append(arg)

    if prompt:
        if len(args[0].strip()) < 1:
            print("Prompt too short. Exiting.")
            sys.exit(1)

    llm_response = ""

    if not chirp_flag:
        if not args:
            # TODO implement args
            print("Did not get necessary arguments.\n")
            print(HELP_DESCRIPTION)
            sys.exit(1)

        if verbose:
            print("Initializing LLM client")

        client_llm = genai.Client(
            vertexai=True, api_key=api_key
        )
        if prompt:
            if verbose:
                print("User used flag --prompt. Overriding TTS transcription")
                
            transcription = args[0]
        else:
            transcription = stt(args[0], verbose)

        llm_response = llm(client_llm, transcription, verbose, LLM_PROMPT)
        if verbose:
            print("Initializing TTS client")

        client_tts = texttospeech.TextToSpeechLongAudioSynthesizeClient(
            credentials=credentials
        )

        tts(client_tts, llm_response, OUTPUT_AUDIO_FILEPATH, verbose)
    else:
        if verbose:
            print("Chirp FLag")
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