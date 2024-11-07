import requests
import tqdm
from pathlib import Path


def download_file(url: str, path: Path, with_progress_bar=True):
    """Downloads a file with a progress bar and saves it to a path"""
    if with_progress_bar:
        print("Downloading " + str(url))
        print("and saving it to " + str(path))
    
    # taken from:
    # https://stackoverflow.com/questions/37573483/progress-bar-while-download-file-over-http-with-requests/37573701
    response = requests.get(url, stream=True)
    total_size_in_bytes = int(response.headers.get("Content-Length", 0))
    block_size = 1024
    progress_bar = tqdm.tqdm(
        total=total_size_in_bytes,
        unit="iB",
        unit_scale=True,
        disable=not with_progress_bar
    )
    with open(path, "wb") as file:
        for data in response.iter_content(block_size):
            progress_bar.update(len(data))
            file.write(data)
    progress_bar.close()
    if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
        raise Exception("File downloading failed.")
