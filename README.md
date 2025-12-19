# chirp‑transcript‑tool  

> **TL;DR** – Turn one or many plain‑text transcripts into natural‑sounding speech, clean the audio, and get word‑level timestamps – all in a single command‑line run.  

The tool stitches together four Google Cloud services such as Vertex AI Gemini, Cloud Text‑to‑Speech (Chirp‑HD‑3), Cloud Storage (buckets) with two open‑source libraries (ffmpeg, WhisperX) and a tiny CLI wrapper that handles flag parsing, cost reporting, and error handling.

---

**Disclaimer:**  
This code was writen as part of a learning project and is not a product software. By using it, modifying, or distributing this code, you acknowledge that you are solely responsible for all outcomes, consequences, and legal obligations arising from your actions. The author(s) and contributors provide no warranty or liability for any misuse, damages, or unintended effects resulting from the code.


## Table of Contents  

1. [Features](#features)  
2. [Presentation](#presentation)
3. [Architecture diagram](#architecture-diagram)  
4. [Prerequisites](#prerequisites)  
5. [Installation (UV)](#installation-uv)  
6. [Configuration (environment variables & `config.py`)](#configuration)  
7. [Command‑line interface](#cli)  
8. [Pipeline walk‑through](#pipeline-walk-through)  
9. [Examples](#examples)  
10. [Cost reporting](#cost-reporting)  
11. [Testing & debugging](#testing--debugging)  
12. [Troubleshooting](#troubleshooting)  
13. [Documentation / Bibliography](#bibliography)  
14. [License](#license)  

---

## Features  

| ✅ | Description |
|----|-------------|
| **LLM‑based transcript polishing** | Optional Gemini‑Pro‑Preview 3 pass that injects punctuation, pauses, and other “human‑like” cues according to the **Chirp‑HD‑3** documentation. |
| **Asynchronous TTS** | Sends asynchronously each (possibly tuned) transcript to **Google Cloud Text‑to‑Speech Long‑Audio** (Chirp‑HD‑3) → stores the result in a Cloud Storage bucket → downloads locally. |
| **Silence removal** | One‑liner ffmpeg `silenceremove` filter trims long pauses, making the final audio sound more natural. |
| **Word‑level timestamps** | WhisperX (large‑v2) produces timestamps (start/end) times for every spoken word. |
| **Batch processing** | Accept a single file, a directory of `.txt` files, or a raw prompt. |
| **Cost awareness** | Token‑based cost for Gemini, character‑based cost for Chirp‑HD‑3, printed per‑file and overall. |
| **UV‑based packaging** | All dependencies declared in `pyproject.toml`; install with the fast, modern `uv` tool. |
| **Extensible flag parser** | `tools/flags_parser.py` validates mutual exclusivity (`--prompt` vs `--from‑file/--from‑dir`). |

---

## Presentation

### Input text (from file)
```text
A lone astronomer set up a telescope on a desert ridge, hoping the clear night sky would reveal a secret. When a faint flicker appeared, the instrument captured a pattern that spelled out a long‑lost melody encoded in starlight. The astronomer smiled, realizing the universe had been humming a song all along, waiting for someone to listen.
```

### Command
```bash
uv run main.py --from-file --no-bucket-preserve --verbose transcriptions/presentation_transcript.txt
```

### Log output
  
```
Initializing TTS client
Reading transcripts
Reading from file: transcriptions/presentation_transcript.txt
Loaded: transcriptions/presentation_transcript.txt
Reading Transcripts Done
Initializing LLM client
Setting LLM client for transcript tuning with model and getting response (gemini-3-pro-preview)
Got response - adding to list of responses

---Response---
A lone astronomer set up a telescope on a desert ridge, hoping the clear night sky would reveal a secret. [pause short] When a faint flicker appeared, the instrument captured a pattern that spelled out a long‑lost melody encoded in starlight. [pause short] The astronomer smiled, realizing the universe had been humming a song all along... waiting for someone to listen.
---------


===OVERALL COST===
Prompt tokens: 2007.0 --- Cost: 0.00802800 $
Response tokens: 75.0 --- Cost: 0.00060000 $
Summary: 2082.0 tokens --- 0.00862800 $
===$$$===

Setting TTS client with model and storage client (Chirp - Sadaltager) and sending request.
Requesting Audio content to bucket: gs://bucket1/response_audio/presentation_transcript_20251219_134905.wav
Audio synthesized to GCS. Downloading: gs://bucket1/response_audio/presentation_transcript_20251219_134905.wav
Blob deleted: response_audio/presentation_transcript_20251219_134905.wav
Finished: presentation_transcript_20251219_134905.wav

===OVERALL COST===
Tokens: 370 --- Cost: 0.011100 $
===$$$===

Running ffmpeg remove silence
Removed silence and saved file to: edited_audio/presentation_transcript_20251219_134905.wav
Done cut silence. Files saved to directory: edited_audio
Loading WhisperX on cuda, batch_size = 8, compute_type = float16
Loading allign model
Transcribing audio
Cleaning memory - transcribe
Generating timestamps
Timestamps for file edited_audio/presentation_transcript_20251219_134905.wav generated.
Cleaning
Transcribing done file saved to timestamped_transcriptions/output.txt
```

### Tuned transcript (by Gemini-3-Pro-Preview)

```text
A lone astronomer set up a telescope on a desert ridge, hoping the clear night sky would reveal a secret. [pause short] When a faint flicker appeared, the instrument captured a pattern that spelled out a long‑lost melody encoded in starlight. [pause short] The astronomer smiled, realizing the universe had been humming a song all along... waiting for someone to listen.
```

### Audio from TTS model (Chirp - voice Sadaltager)

🎵 [Click here to listen to the audio player](https://archbober.github.io/chirp-transcript-tool/audio_response.html)

### Audio after removing silence

🎵 [Click here to listen to the audio player](https://archbober.github.io/chirp-transcript-tool/audio_edit.html)

### Transcript with timestamps from file (per word for now in List[dict[str,str]] form)
```
[{'word': 'A', 'start': np.float64(0.031), 'end': np.float64(0.613)}, {'word': 'lone', 'ord': 'pattern', 'start': np.float64(9.301), 'end': np.float64(9.642)}, ... -> ... {'word': 'listen.', 'start': np.float64(18.55), 'end': np.float64(19.052)}]
```

---

## Architecture Diagram

```
┌─────────────────────┐
│ Input (txt / prompt)│
└─────────┬───────────┘
          ▼
┌─────────────────────┐
│   read_transcripts  │
└─────────┬───────────┘
          ▼
┌───────────────────────────────────────┐
│   Is LLM tuning enabled? (–no‑tuning) │
└───────┬───────────────────────┬───────┘
        │                       │
   Yes  ▼                       ▼   No
 ┌─────────────────────┐   ┌─────────────────────┐
 │      llm()          │   │ (skip tuning step)  │
 │(Gemini‑Pro‑Preview3)│   │                     │
 └───────┬─────────────┘   └───────┬─────────────┘
         │                         │
         ▼                         │
 ┌─────────────────────┐           │
 │  Async  tts_chirp() │◄──────────┘
 │ (Google TTS – Chirp)│   
 │  → upload to GCS    │   
 │      (bucket)       │
 └───────┬─────────────┘  
         │                         
         ▼                         
 ┌─────────────────────┐   
 │       Async         │
 │ Download from GCS   │   
 └───────┬─────────────┘ 
         │                         
         ▼                         
 ┌─────────────────────┐  
 │   ffmpeg_cutter()   │  
 │ (remove long pauses)│   
 └───────┬─────────────┘   
         │     
         ▼     
 ┌─────────────────────┐
 │ stt_timestamps()    │   
 │     WhisperX        │
 │    word‑level       │
 │    timestamps       │   
 └─────────────────────┘   
 ```

 ## Prerequisites  

| Item | Minimum version / notes |
|------|------------------------|
| **Python** | 3.13 (declared in `pyproject.toml`) |
| **UV** | `uv >=0.4` – the recommended installer for the project |
| **ffmpeg** | Must be on the system `$PATH` (`ffmpeg -version` works) |
| **GPU (optional)** | CUDA‑enabled GPU for WhisperX speed‑up; otherwise CPU fallback works (slower) |
| **Google Cloud project** | Vertex AI, Cloud Storage, Cloud Text‑to‑Speech APIs enabled |
| **Service‑account JSON** | With roles `aiplatform.user`, `storage.objectAdmin`, `texttospeech.admin` |

---

## Installation (UV)  

```bash
# 1️⃣ Clone the repo
git clone https://github.com/ArchBober/chirp-transcript-tool.git
cd chirp-transcript-tool

# 2️⃣ Install UV (if you don’t have it yet)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 3️⃣ Create an isolated environment and install deps
uv venv .venv               # creates .venv/
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 4️⃣ Install the package (reads pyproject.toml)
uv sync                     # resolves & installs all dependencies
```

> **Why UV?**  
> UV resolves the dependency graph **much faster** than `pip` and writes a lockfile (`uv.lock`) that guarantees reproducible builds. It also respects the `[project]` table from `pyproject.toml`, so you don’t need a separate `requirements.txt`.

## Configuration  

### Environment variables (`.env`)  

Create a file named `.env` in the repository root:

```dotenv
VERTEX_AI_API_KEY=<your‑vertex‑api‑key>
SECRET_JSON_FILEPATH=/absolute/path/to/service-account.json
BUCKET_NAME=<your‑gcs‑bucket>
```

The script loads these with `python-dotenv`.  

### `config.py` (already shipped)  

| Constant | Meaning |
|----------|---------|
| `TTS_TEXT_FILE` | Default transcript used when no file flag is supplied. |
| `OUTPUT_AUDIO_DIR` / `EDITED_AUDIO_DIR` | Where raw and cleaned audio are stored locally. |
| `SPEAKING_RATE` | Default 1.0× (range 0.5‑2.0). |
| `TTS_VOICE` | `"Sadaltager"` – a Chirp‑HD‑3 voice. |
| `LANGUAGE` | `"en‑US"` – language code for TTS. |
| `LLM_MODEL` | `"gemini-3-pro-preview"` – the Gemini model used for tuning. (can be changed to cheaper one model) |
| `LLM_CHIRP_PROMPT` | Prompt that injects the **Chirp‑HD‑3** scripting guidelines (see `descriptions/prompt_chirp_doc.py` and `config.py`). |
| `LLM_INPUT_TOKEN_PRICE`, `LLM_OUTPUT_TOKEN_PRICE`, `TTS_CHIRP_TOKEN_PRICE` | Pricing constants (USD per M tokens/characters). Update them if Google changes its rates. |

### Prompt documentation (`descriptions/prompt_chirp_doc.py` && `config.py`)  

Contains the full “Scripting and prompting tips” you posted – the LLM uses this to add natural‑speech cues without altering the original meaning.

## Command‑line interface  

Run the entry point with `uv run main.py`. Flags are defined in `tools/flags_parser.py`.

| Flag | Alias | Description |
|------|-------|-------------|
| `--verbose` | – | Print detailed progress and cost info. |
| `--cost-single` | – | Show per‑file TTS cost. |
| `--prompt` | – | First positional argument is treated as a raw prompt (no file reading). |
| `--no‑tuning` | – | Skip the Gemini LLM step; feed transcripts straight to TTS. |
| `--no‑bucket‑preserve` | – | Delete the temporary audio object from Cloud Storage after download. |
| `--from‑file` | – | Load a **single** transcript file (default path or `TTS_TEXT_FILE`). |
| `--from‑dir` | – | Load **all** `.txt` files from the supplied directory. |
| `--help` | – | Show the help description (`HELP_DESCRIPTION`). |
| `positional` | – | Remaining arguments – either the prompt text (`--prompt`) or the path(s) for `--from‑file/--from‑dir`. |

**Mutual exclusions** (enforced by the parser):

* `--prompt` cannot be combined with `--from‑file` or `--from‑dir`.  
* `--from‑file` and `--from‑dir` cannot be used together.

## Pipeline walk‑through  

1. **Parse flags** – `tools/flags_parser.parse_flags()` validates the command line.  
2. **Read transcripts** – `tools/read_transcripts.py` loads one file or an entire directory into a `Dict[str,str]`.  
3. **LLM tuning (optional)** – `model_tools/llm.py` sends each transcript to Gemini (`genai.Client`). The system prompt (`LLM_CHIRP_PROMPT`) forces the model to only add punctuation/pauses/IPA tags described in the Chirp documentation.  
4. **Asynchronous TTS** – `model_tools/tts_chirp.py`  
   * Calls `texttospeech.TextToSpeechLongAudioSynthesizeAsyncClient` with the refined text.  
   * Stores the generated WAV in the bucket (`gs://<BUCKET>/<OUTPUT_AUDIO_DIR>/…`).  
   * Downloads the file locally, optionally deleting the bucket object (`--no‑bucket‑preserve`).  
5. **Silence removal** – `tools/ffmpeg_cutter.py` runs `ffmpeg -af silenceremove=stop_periods=-1:stop_duration=0.2:stop_threshold=-40dB` removing silence longer than 0.2s and quiter than -40 dB (if those parameters are not changed by user).  
6. **Timestamp extraction** – `model_tools/stt.py` loads WhisperX (large‑v2) on the cleaned audio, aligns word‑level timestamps, and writes them to `timestamped_transcriptions/output.txt`. Model can be changed. Also this library is very problematic so its worth to look on whisperx issue page if there will be some problems with environment/downloading etc.  

All heavy‑weight I/O (bucket upload/download, TTS requests) is performed **asynchronously** with `asyncio.gather`, dramatically reducing total runtime for multi‑file batches (if not async it would do 1 file at a time which is quite long especially if many heavy inputs are delivered). That means max time waiting for TTS execution = largest file. 

## Examples  

### 1️⃣ Prompt → LLM → TTS → Clean → Timestamps  

```bash
export VERTEX_AI_API_KEY=abcd123...890xyz
export SECRET_JSON_FILEPATH=$HOME/gcloud/key.json
export BUCKET_NAME=chirp-audio-bucket

uv run main.py \
    --prompt \
    --verbose \
    "What is lorem ipsum."

```

**What you get**

* `response_audio/name_<timestamp>.wav` – raw Chirp synthesis.  
* `edited_audio/name_<timpestamp>.wav` – silence‑removed version.  
* `timestamped_transcriptions/output.txt` – JSON‑like list of `{word,start,end}`. (for now later add more options/ better option to save timestamps)

### 2️⃣ Batch directory, skip LLM, keep bucket objects  

```bash
uv run main.py \
    --from-dir \
    --no-tuning \
    --cost-single ./my_transcripts

```

Processes every `*.txt` under `./my_transcripts`, prints per‑file TTS cost, and leaves the intermediate objects in the bucket (useful for later inspection).

### 3️⃣ Using a file not preserving copy on bucket and disabling tuning (skip LLM)  

```bash
uv run main.py \
    --from-file \
    --no-bucket-preserve \
    --no-tuning ./script.txt
```

## Cost reporting  

When `--verbose` (or `--cost-single`) is active the script prints three sections:

| Section | What is shown |
|---------|---------------|
| **LLM cost** | `prompt tokens × LLM_INPUT_TOKEN_PRICE` and `response tokens × LLM_OUTPUT_TOKEN_PRICE`. |
| **TTS cost** | `character count × TTS_CHIRP_TOKEN_PRICE`. |
| **Overall** | Sum of the above for the whole run. |

The numbers are **USD** (based on the constants in `config.py`). Adjust the constants if Google updates its pricing.

## Troubleshooting  

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `ffmpeg: command not found` | ffmpeg not installed or not on `$PATH`. | Install via `apt-get install ffmpeg`, `brew install ffmpeg`, or download from https://ffmpeg.org/. |
| `google.api_core.exceptions.PermissionDenied` | Service‑account lacks required IAM roles. | Grant `roles/aiplatform.user`, `roles/texttospeech.admin`, `roles/storage.objectAdmin` to the service account. |
| `Operation timed out` while waiting for TTS | Very long transcript (> 50 k characters) or network latency. | Split the transcript into smaller chunks (≤ 5000 chars) before calling `tts_chirp()` or set higher timeout in tts_chrip.py ex. -> await operation.result(timeout=600). |
| WhisperX runs on CPU and is extremely slow | No CUDA device detected. | Install CUDA drivers and the matching `torch` wheel ex. -> (`uv add torch --extra-index-url https://download.pytorch.org/whl/cu121`). But for sanity its worth checking whisperx repository for solutions. |
| Empty `output.txt` after STT | Audio file never downloaded or corrupted. | Verify that `ffmpeg_cutter` produced a non‑zero‑size WAV; re‑run with `--verbose` to see the download URI. |
| `--prompt` and `--from-dir` used together → script exits | Parser correctly aborts. | Choose one mode only – either a raw prompt or a directory of files. |

## Bibliography  

| # | Resource | Link |
|---|----------|------|
| 1 | **Google Vertex AI – Gemini Pro Preview** (LLM used for transcript polishing) | <https://docs.cloud.google.com/vertex-ai/docs/start/introduction-unified-platform> |
| 2 | **Google Cloud Text‑to‑Speech – Chirp HD 3** (high‑quality neural voice) | <https://docs.cloud.google.com/text-to-speech/docs/chirp3-hd> |
| 3 | **Google Cloud Storage** (temporary bucket for long‑audio synthesis) | <https://docs.cloud.google.com/storage/docs> |
| 4 | **ffmpeg – silenceremove filter** (removing long pauses) | <https://ffmpeg.org/ffmpeg-filters.html#silenceremove> |
| 5 | **WhisperX – word‑level timestamps** (open‑source speech‑to‑text) | <https://github.com/m-bain/whisperX> |
| 6 | **UV – a fast Python package manager** | <https://github.com/astral-sh/uv> |
| 7 | **python‑dotenv** (loading `.env` files) | <https://pypi.org/project/python-dotenv/> |
| 8 | **Google‑GenAI Python SDK** (client for Gemini) | <https://pypi.org/project/google-genai/> |
| 9 | **Google‑Cloud‑Text‑to‑Speech Python client** | <https://pypi.org/project/google-cloud-texttospeech/> |
|10| **Google‑Cloud‑Storage Python client** | <https://pypi.org/project/google-cloud-storage/> |
|11| **OpenAI‑Whisper** (fallback STT model used by WhisperX) | <https://github.com/openai/whisper> |
|12| **Prompt engineering guide for Chirp** (the large block you supplied) | *Embedded in `descriptions/prompt_chirp_doc.py`* |

## License  

This project is released under the **MIT License**. See the `LICENSE` file for full terms.

---  

*Enjoy turning text into natural‑sounding audio!* 🚀