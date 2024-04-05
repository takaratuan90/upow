import torch
import torch.nn as nn
import torch.optim as optim
from data_handling.load_data import load_data
from training.train_model import train_model
import os
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s:%(levelname)s - %(message)s"
)


class SimpleModel(nn.Module):
    def __init__(self):
        super(SimpleModel, self).__init__()
        self.fc = nn.Linear(10, 1)

    def forward(self, x):
        return self.fc(x)


def train_and_contribute(miner_id, zip_file_path, folder):
    data_loader = load_data(zip_file_path)

    model = SimpleModel()
    logging.info("Training initiated locally..")

    train_model(model, data_loader)

    if any(param.grad is None for param in model.parameters()):
        print(f"Miner {miner_id} failed to compute gradients...")
        return

    destination_folder = "./Destination"
    gradients = [param.grad.data.numpy().tolist() for param in model.parameters()]
    gradients_folder = os.path.join(destination_folder, folder)
    os.makedirs(gradients_folder, exist_ok=True)

    torch.save(
        model.state_dict(),
        os.path.join(gradients_folder, f"{miner_id}.pth"),
    )
    logging.info("Training Completed...")
    return gradients
