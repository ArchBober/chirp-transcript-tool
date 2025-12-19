HELP_DESCRIPTION = '''Usage: python -m main [OPTIONS] [ARGS...]

A pipeline that converts text transcripts (or a raw prompt) into natural-sounding
audio using Google Chirp HD-3, removes long pauses with ffmpeg, and extracts
word-level timestamps with WhisperX.

Options:
  --verbose                Enable verbose output - prints progress, token counts,
                           cost breakdowns, and detailed debug information.

  --cost-single            Show the per-file cost  (useful for budgeting).

  --prompt                 Treat the first positional argument as a raw prompt
                           (no transcript file is read). Mutually exclusive
                           with --from-file and --from-dir.

  --no-tuning              Skip the Gemini LLM refinement step. The raw
                           transcript is sent directly to the TTS engine.

  --no-bucket-preserve     Delete the intermediate audio object from the Cloud
                           Storage bucket after it has been downloaded locally.

  --from-file              Load a single transcript file (default path is
                           `transcriptions/tts_default.txt` if no positional
                           argument is supplied).

  --from-dir               Load **all** `.txt` files from the supplied
                           directory. Each file is processed independently.

  --help                   Show this help message and exit.

Positional arguments:
  ARGS...                  When --prompt is used, the first argument is the
                           prompt text. When --from-file or --from-dir is used,
                           the argument is the path to the file or directory.

Examples:
  # 1 Prompt → LLM → TTS → clean → timestamps
  uv run main.py --prompt "Explain quantum entanglement in simple terms."

  # 2 Batch processing of a directory, skip LLM tuning and show cost per file
  uv run main.py --from-dir --no-tuning --cost-single ./my_transcripts

  # 3 Use a specific file and delete the bucket copy after download
  uv run main.py --from-file --no-bucket-preserve ./script.txt

Notes:
  • --prompt cannot be combined with --from-file or --from-dir.
  • --from-file and --from-dir are mutually exclusive.
  • All Google Cloud credentials are read from the `.env` file (VERTEX_AI_API_KEY,
    SECRET_JSON_FILEPATH, BUCKET_NAME).
''' 