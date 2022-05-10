from collections import OrderedDict

import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.transforms as transforms
from torch.utils.data import DataLoader
from torchvision.datasets import CIFAR10
import numpy as np

DEVICE = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
CONSENSUS_SIZE = 10

class ShuffleDataset(torch.utils.data.Dataset):
    def __init__(self, dataset):
        super().__init__()
        self.orig_dataset = dataset
        self.shuffled_idxes = np.random.permutation(len(dataset))

    def __getitem__(self, i):
        return self.orig_dataset[self.shuffled_idxes[i]]

    def __len__(self):
        return len(self.orig_dataset)


class SliceDataset(torch.utils.data.Dataset):
    def __init__(self, dataset, start, end):
        super().__init__()
        self.orig_dataset = dataset
        self.start = start
        self.end = end

    def __getitem__(self, i):
        if i >= self.end:
            raise IndexError('list index out of range')
        return self.orig_dataset[i + self.start]

    def __len__(self):
        return self.end - self.start


def load_data(num_clients):
    """Load CIFAR-10 (training and test set)."""
    transform = transforms.Compose(
        [transforms.ToTensor(), transforms.Normalize(
            (0.5, 0.5, 0.5), (0.5, 0.5, 0.5))]
    )

    trainset = CIFAR10(".", train=True, download=True, transform=transform)
    trainset = ShuffleDataset(trainset)
    testset = CIFAR10(".", train=False, download=True, transform=transform)
    testset = ShuffleDataset(testset)
    train_len = len(trainset) // num_clients
    test_len = len(testset) // num_clients
    trainloaders = []
    testloaders = []
    num_examples = []

    for i in range(num_clients):
        train_subset = SliceDataset(trainset, i * train_len, (i+1) * train_len)
        test_subset = SliceDataset(testset, i * test_len, (i+1) * test_len)
        trainloaders.append(DataLoader(
            train_subset, batch_size=32, shuffle=True))
        testloaders.append(DataLoader(test_subset, batch_size=32))
        num_examples.append(
            {"trainset": len(train_subset), "testset": len(test_subset)})

    #num_examples = {"trainset" : len(trainset), "testset" : len(testset)}
    return trainloaders, testloaders, num_examples

class Net(nn.Module):
    def __init__(self) -> None:
        super(Net, self).__init__()
        self.conv1 = nn.Conv2d(3, 6, 5)
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(6, 16, 5)
        self.fc1 = nn.Linear(16 * 5 * 5, 120)
        self.fc2 = nn.Linear(120, 84)
        self.fc3 = nn.Linear(84, 10)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = x.view(-1, 16 * 5 * 5)
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x


# Load model and data
# net = Net().to(DEVICE)
trainloaders, testloaders, num_examples = load_data(CONSENSUS_SIZE)

