import json
import config.config as config
import websockets
import asyncio
import logging
import argparse
import os
import base58


from training.train_and_contribute import train_and_contribute
from data_handling.jobDownload import download_zip
from job_management.getJob import get_first_zip_in_job
from job_management.deleteJob import delete_jobid_folder_and_file, clear_directory
from utils.getGradient import find_gradient
from job_management.sendGradient import send_file_via_websocket
from job_management.requestJob import request_job_file

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s:%(levelname)s - %(message)s"
)


class MessageType:
    GRADIENT = "gradient"
    REQUESTFILE = "requestFile"
    DOWNLOADFILE = "downloadFile"
    PING = "ping"


def parse_args():
    parser = argparse.ArgumentParser(description="Miner Configuration")
    parser.add_argument(
        "--MINER_POOL_IP", required=True, help="IP address of the miner pool"
    )
    parser.add_argument(
        "--MINER_POOL_PORT", required=True, type=int, help="Port of the miner pool"
    )
    parser.add_argument(
        "--WALLET_ADDRESS", required=True, help="Wallet address for the miner"
    )
    return parser.parse_args()


async def ping_server(message_type, find_gradient, download_zip):
    uri = f"ws://{config.MINER_POOL_IP}:{config.MINER_POOL_PORT}"
    print("uri", uri)
    try:
        async with websockets.connect(uri) as websocket:
            # Send a ping message
            message = {
                "type": MessageType.PING,
            }

            await websocket.send(json.dumps(message))

            # Wait for a response
            response = await websocket.recv()
            if response.startswith("SUCCESS") or response.startswith("ERROR"):
                logging.info("Pool response: %s", response)

            request_response = await request_job_file(
                websocket, MessageType.REQUESTFILE
            )
            if request_response.startswith("SUCCESS") or request_response.startswith(
                "ERROR"
            ):
                logging.info("Pool response: %s", request_response)

            try:
                # Parse the JSON response into a Python dictionary
                response_data = json.loads(request_response)

                print("response_data", response_data)

                # Handle double encoded JSON
                if isinstance(response_data, str):
                    response_data = json.loads(response_data)

                if (
                    isinstance(response_data, dict)
                    and response_data.get("message_type") == MessageType.DOWNLOADFILE
                ):
                    url = response_data.get("url")
                    file_hash = response_data.get("file_hash")
                    jobname = response_data.get("active_mining_value")
                    value = download_zip(url, jobname, file_hash)

                    if value:
                        folder, zip_file, file_name = get_first_zip_in_job("job")
                        if folder and zip_file:
                            miner_id = file_name
                            path = f"./job/{folder}/{zip_file}"
                            gradient = train_and_contribute(miner_id, path, folder)
                            logging.info("Gradient %s", gradient)
                            delete_jobid_folder_and_file("job", folder, zip_file)
                        else:
                            logging.info("No folder or zip file found to Train")
                else:
                    logging.info("Error: Response data is not a valid JSON object.")

            except json.JSONDecodeError:
                logging.error("Error: Could not decode JSON response.")
            except TypeError:
                logging.error("TypeError: The response is not in the expected format.")
            except AttributeError:
                logging.error("AttributeError: Unexpected data type.")

            fld, fil, just_name = find_gradient("Destination")
            if fld and fil:
                file_path = f"./Destination/{fld}/{fil}"
                if message_type == MessageType.GRADIENT:
                    file_response = await send_file_via_websocket(
                        websocket, file_path, MessageType.GRADIENT, just_name, fld
                    )

                    if file_response.startswith("SUCCESS") or file_response.startswith(
                        "ERROR"
                    ):
                        logging.info("Pool response: %s", file_response)

                    if file_response:
                        delete_jobid_folder_and_file("Destination", fld, fil)
                    else:
                        logging.info("Gradient failed to be sent")
            else:
                logging.info("No gradient file found to send.")

    except websockets.ConnectionClosedError:
        logging.error(
            "ConnectionClosedError: The websocket connection is closed unexpectedly."
        )
    except websockets.WebSocketException as e:
        logging.error(
            "WebSocketException: An error occurred with the websocket connection. Details: %s",
            e,
        )
    except Exception as e:
        logging.error("An unexpected error occurred: %s", e)


def ensure_directory_exists(directory_path):
    """Ensure that a directory exists; if it doesn't, create it."""
    if not os.path.exists(directory_path):
        logging.info(f"creating {directory_path}")
        os.makedirs(directory_path)


def is_valid_address(address: str) -> bool:
    try:
        _ = bytes.fromhex(address)
        return len(address) == 128
    except ValueError:
        try:
            decoded_bytes = base58.b58decode(address)
            if len(decoded_bytes) != 33:
                return False
            specifier = decoded_bytes[0]
            if specifier not in [42, 43]:
                return False
            return True
        except ValueError:

            return False
    except Exception as e:
        print(f"Error validating address: {e}")
        return False


async def start_server(find_gradient, download_zip):
    logging.info("Starting Miner...")
    try:
        while True:
            try:
                await ping_server(MessageType.GRADIENT, find_gradient, download_zip)
            except Exception as e:
                logging.error("Miner closed due to an error: %s", e, exc_info=True)
                break
            await asyncio.sleep(config.INTERVAL)
    except KeyboardInterrupt:
        logging.info("Miner shutdown initiated by user.")
    finally:
        logging.info("Shutting down Miner...")


try:
    ensure_directory_exists("./Destination/")
    ensure_directory_exists("./job/")

    clear_directory("./Destination/")
    clear_directory("./job/")
    args = parse_args()

    if not is_valid_address(args.WALLET_ADDRESS):
        logging.error(
            "Invalid wallet address provided. Please provide a valid address."
        )
        raise ValueError(
            "Invalid wallet address provided. Please provide a valid address."
        )
    else:
        # Override config values with command-line arguments
        config.MINER_POOL_IP = args.MINER_POOL_IP
        config.MINER_POOL_PORT = args.MINER_POOL_PORT
        config.WALLET_ADDRESS = args.WALLET_ADDRESS
        asyncio.get_event_loop().run_until_complete(
            start_server(find_gradient, download_zip)
        )
except KeyboardInterrupt:
    logging.info("Miner shutdown process complete.")
