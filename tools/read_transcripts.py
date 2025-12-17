from pathlib import Path

def _read_file(path: str | Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"The file '{path}' does not exist.")
    if not path.is_dir():
        raise IsADirectoryError(f"{path} is a directory file path. Use flag --from-dir to read all files from this path.")
    if path.suffix.lower() != ".txt":
        raise InvalidExtensionError(f"The file '{path}' does not have a .txt extension.")
    
    try:
        return path.read_text(encoding="utf-8")

    except UnicodeDecodeError:
        return p.read_text()

    return transcription

def read_transcripts(path: str | Path, dir_flag: bool) -> Dict[str, object]:
    txt_contents: Dict[str, object] = {}
    base = Path(dir_path)

    if dir_flag:
        if not base.is_dir():
            raise NotADirectoryError(f"{base} is not a valid directory")

        for txt_file in sorted(base.glob("*.txt")):
            txt_contents[txt_file.name] = _read_file(path)

    else:
       txt_contents[txt_file.name] = _read_file(path)

    return txt_contents


