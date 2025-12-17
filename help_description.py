HELP_DESCRIPTION = '''AI Speak-Think-Play Tool 0.1.0 for communicating with LLM model through audio file or prompt and getting speech response. 
Designed mainly for polishing speaking in foreign languages with small privacy upgrade by using local Speech-To-Text (STT) model but can also be used for other purposes. 
LLM and Text-To-Speech model is designed at the moment to use Gemini available models. 
To use this project user needs to have set API key for Vertex AI service (set in .env under VERTEX_AI_API_KEY) and have OAuth2 secret json file available from Google Cloud services by setting up project and activating TTS api (json filepath need to be in .env under SECRET_JSON_FILEPATH).
This is testing/learning project and by that i'm not taking responsibility for other users actions using this code. 
By using/editing this code you take full responsibility for your actions and potential negative effects (ex. high token consuption, restricted GC services and more).

[Usage]
    uv run main.py [options] <input-audio-filepath>
    uv run main.py [options] --prompt "<your prompt text>"

[Options]
    --help - Show this text.
    --prompt - Add own prompt in "" to override stt audio reanscription from file.
    --verbose - Show logs and additional info in cli.

[Examples]
    # Normal usage - record from microphone or load an audio file
    uv run main.py "audiofile.mp3"

    # Supply a custom prompt instead of transcribing audio
    uv run main.py --prompt "Explain quantum entanglement in plain English."

    # Get verbose output for debugging
    uv run main.py "audiofile.mp3" --verbose
''' 