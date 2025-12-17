

def read_transcript():
    try:
        with open(TTS_TEXT_FILE, 'r', encoding='utf-8') as f:
            transcription = f.read()
            if verbose:
                print(f"Text file opened and read: {TTS_TEXT_FILE}")

    except FileNotFoundError:
        print(f"The file '{file_path}' was not found. Check the path and try again.")
    except IOError as e:
        print(f"An I/O error occurred: {e}")