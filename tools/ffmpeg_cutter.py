from typing import List

import subprocess, shlex

def cut_silence(filepaths: List[str], safe_dir: str, verbose: bool = False):
    savepaths = []
    if verbose:
        print("Running ffmpeg remove silence")

    for file in filepaths:
        filename = file.split('/')[-1]
        savepath = safe_dir + '/' + filename
        subprocess.run(
            shlex.split(f'ffmpeg -y -i {file} -af silenceremove=stop_periods=-1:stop_duration=0.2:stop_threshold=-40dB {savepath}'),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        check=True)

        savepaths.append(savepath)

        if verbose:
            print(f"Removed silence and saved file to: {savepath}")

    if verbose:
        print(f"Done cut silence. Files saved to directory: {safe_dir}")

    return savepaths