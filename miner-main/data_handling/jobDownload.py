import os
import requests
from requests.exceptions import HTTPError
from tqdm import tqdm


def download_zip(url, jobid, file_hash):
    try:
        job_folder_path = os.path.join(os.getcwd(), "job")
        os.makedirs(job_folder_path, exist_ok=True)

        folder_path = os.path.join(job_folder_path, jobid)
        os.makedirs(folder_path, exist_ok=True)

        file_name = f"{file_hash}.zip"

        file_path = os.path.join(folder_path, file_name)

        if os.path.exists(file_path):
            raise FileExistsError(
                f"The file {file_name} already exists in the directory {folder_path}."
            )

        response = requests.get(url, stream=True)
        response.raise_for_status()

        total_size = int(response.headers.get("content-length", 0))
        block_size = 1024

        with open(file_path, "wb") as file, tqdm(
            desc="Downloading Job",
            total=total_size,
            unit="iB",
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
            for data in response.iter_content(block_size):
                bar.update(len(data))
                file.write(data)

        return True

    except HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except FileExistsError as file_err:
        print(file_err)
    except Exception as err:
        print(f"An error occurred: {err}")
