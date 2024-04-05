import os
import json
from tqdm import tqdm
import config.config as config


async def send_file_via_websocket(websocket, file_path, message_type, just_name, fld):
    try:
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return

        folder_name = os.path.dirname(file_path)
        file_name = os.path.basename(file_path)

        file_size = os.path.getsize(file_path)

        message = {
            "type": message_type,
            "folder_name": folder_name,
            "file_name": file_name,
            "file_data": None,
            "just_name": just_name,
            "job_name": fld,
            "wallet_address": config.WALLET_ADDRESS,
        }

        with open(file_path, "rb") as file:
            with tqdm(
                total=file_size, unit="B", unit_scale=True, desc="Sending File"
            ) as pbar:
                while True:
                    chunk = file.read(65536)
                    if not chunk:
                        break

                    message["file_data"] = chunk.decode("latin1")
                    await websocket.send(json.dumps(message))
                    pbar.update(len(chunk))

        message["file_data"] = "EOF"
        await websocket.send(json.dumps(message))

        response = await websocket.recv()
        return response

    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except OSError as e:
        print(f"Error opening file: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
