from pathlib import Path

from typing import Dict

def _read_file(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"The file '{path}' does not exist.")
    if path.suffix.lower() != ".txt":
        raise InvalidExtensionError(f"The file '{path}' does not have a .txt extension.")
    
    try:
        return path.read_text(encoding="utf-8")

    except UnicodeDecodeError:
        return p.read_text()

    return transcription

def read_transcripts(path: str | Path, dir_flag: bool, verbose: bool = False) -> Dict[str, str]:
    txt_contents: Dict[str, object] = {}
    base = Path(path)

    if verbose:
        print("Reading transcripts")

    if dir_flag:
        if verbose:
            print(f"Reading transcripts from firectory: {path}")
        if not base.is_dir():
            raise NotADirectoryError(f"{base} is not a valid directory")

        for txt_file in sorted(base.glob("*.txt")):
            if verbose:
                print(f"Loaded: {txt_file.name}")
            txt_contents[txt_file.name] = _read_file(txt_file)

    else:
        if verbose:
            print(f"Reading from file: {path}")
        txt_contents[path.split('/')[-1]] = _read_file(base)
        if verbose:
                print(f"Loaded: {path}")

    if verbose:
            print(f"Reading Transcripts Done")
    return txt_contents


