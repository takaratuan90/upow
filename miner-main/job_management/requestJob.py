import json
import config.config as config
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s:%(levelname)s - %(message)s"
)


async def request_job_file(websocket, message_type):
    try:
        message = {
            "type": message_type,
            "wallet_address": config.WALLET_ADDRESS,
        }
        logging.info("Requesting a job from Inode..")
        await websocket.send(json.dumps(message))

        response = await websocket.recv()
        return response

    except Exception as e:
        print(f"An error occurred: {e}")
