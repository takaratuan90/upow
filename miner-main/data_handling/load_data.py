import torch


def load_data(zip_file_path):
    num_samples = 100
    num_features = 10
    inputs = torch.randn(num_samples, num_features)
    targets = torch.randn(num_samples, 1)

    data_loader = torch.utils.data.DataLoader(
        torch.utils.data.TensorDataset(inputs, targets), batch_size=32, shuffle=True
    )

    return data_loader
