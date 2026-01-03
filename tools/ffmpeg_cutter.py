from typing import List
import os

import subprocess, shlex

def cut_silence(filepaths: List[str], save_dir: str, verbose: bool = False):
    if verbose:
        print("Running ffmpeg remove silence")
        
    savepaths = []
    os.makedirs(save_dir, exist_ok=True)

    for file in filepaths:
        filename = file.split('/')[-1]

        save_file_dir = save_dir + '/' + filename.split('.')[0]
        os.makedirs(save_file_dir, exist_ok=True)

        savepath = save_file_dir + '/' + filename

        subprocess.run(
            shlex.split(f'ffmpeg -y -i {file} -af silenceremove=stop_periods=-1:stop_duration=0.2:stop_threshold=-40dB {savepath}'),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        check=True)

        savepaths.append(savepath)

        if verbose:
            print(f"Removed silence and saved file to: {savepath}")

    if verbose:
        print(f"Done cut silence. Files saved to directory: {save_dir}")

    return savepaths