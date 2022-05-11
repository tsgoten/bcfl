from collections import OrderedDict
from pickle import TRUE

import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.transforms as transforms
from torch.utils.data import DataLoader
from torchvision.datasets import CIFAR10
import pandas as pd
import numpy as np

DEVICE = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
NUM_CLIENTS = 3
class ShuffleDataset(torch.utils.data.Dataset):
    def __init__(self, dataset):
        super().__init__()
        self.orig_dataset = dataset
        self.shuffled_idxes = np.random.permutation(len(dataset))
        self.data = self.orig_dataset.data
        self.targets = self.orig_dataset.targets
    
    def __getitem__(self, i):
        return self.orig_dataset[self.shuffled_idxes[i]]
    def __len__(self):
        return len(self.orig_dataset)


class SliceDataset(torch.utils.data.Dataset):
    def __init__(self, dataset, start, end):
        super().__init__()
        self.orig_dataset = dataset
        self.data = self.orig_dataset.data
        self.targets = self.orig_dataset.targets
        self.start = start
        self.end = end

    def __getitem__(self, i):
        if i >= self.end:
            raise IndexError('list index out of range')
        return self.orig_dataset[i + self.start]

    def __len__(self):
        return self.end - self.start

    def to_csv(self, fname):
        data = self.orig_dataset.data[self.start:self.end]
        data = data.reshape([data.shape[0], -1])
        targets = np.array(self.orig_dataset.targets[self.start:self.end]).reshape([-1, 1])
        data = np.concatenate([data, targets], axis=1)
        data = pd.DataFrame(data=data, index=None, columns=None)
        data.to_csv(fname)

def load_data(num_clients, bag=True, seed=None):
    """Load CIFAR-10 (training and test set)."""
    transform = transforms.Compose(
    [transforms.ToTensor(), transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))]
    )
    np.random.seed(seed) 
    trainset = CIFAR10(".", train=True, download=True, transform=transform)

    orig_trainset = ShuffleDataset(trainset)
    trainset = orig_trainset
    testset = CIFAR10(".", train=False, download=True, transform=transform)
    orig_testset = ShuffleDataset(testset)
    testset = orig_testset
    train_len = len(trainset) // num_clients
    test_len = len(testset) // num_clients
    trainloaders = []
    testloaders = []
    num_examples = []
         
    for i in range(num_clients):
        train_subset = SliceDataset(trainset, i * train_len, (i+1) * train_len)
        test_subset = SliceDataset(testset, i * test_len, (i+1) * test_len)
        train_subset.to_csv("datasets/cifar10_train_{}.csv".format(i))
        trainloaders.append(DataLoader(train_subset, batch_size=32, shuffle=True))
        testloaders.append(DataLoader(test_subset, batch_size=32))
        num_examples.append({"trainset" : len(train_subset), "testset" : len(test_subset)})
        if bag:
            trainset = ShuffleDataset(orig_trainset)
            testset = ShuffleDataset(orig_testset)
        
    return trainloaders, testloaders, num_examples

def train(net, trainloader, epochs):
    """Train the network on the training set."""
    criterion = torch.nn.CrossEntropyLoss()
    optimizer = torch.optim.SGD(net.parameters(), lr=0.001, momentum=0.9)
    for _ in range(epochs):
        for images, labels in trainloader:
            images, labels = images.to(DEVICE), labels.to(DEVICE)
            optimizer.zero_grad()
            loss = criterion(net(images), labels)
            loss.backward()
            optimizer.step()

def validate(net, trainloader):
    """Validate the network on the entire train set."""
    criterion = torch.nn.CrossEntropyLoss()
    correct, total, loss = 0, 0, 0.0
    with torch.no_grad():
        for data in trainloader:
            images, labels = data[0].to(DEVICE), data[1].to(DEVICE)
            outputs = net(images)
            loss += criterion(outputs, labels).item()
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
    accuracy = correct / total
    return loss, accuracy    

def test(net, testloader):
    """Validate the network on the entire test set."""
    criterion = torch.nn.CrossEntropyLoss()
    correct, total, loss = 0, 0, 0.0
    with torch.no_grad():
        for data in testloader:
            images, labels = data[0].to(DEVICE), data[1].to(DEVICE)
            outputs = net(images)
            loss += criterion(outputs, labels).item()
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
    accuracy = correct / total
    return loss, accuracy


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
trainloaders, testloaders, num_examples = load_data(NUM_CLIENTS, bag=True, seed=42)


class CifarClient():

    def __init__(self, client_id):
        self.client_id = client_id
        self.net = Net().to(DEVICE)

    def get_parameters(self):
        return [val.cpu().numpy() for _, val in self.net.state_dict().items()]

    def set_parameters(self, parameters):
        params_dict = zip(self.net.state_dict().keys(), parameters)
        state_dict = OrderedDict({k: torch.tensor(v) for k, v in params_dict})
        self.net.load_state_dict(state_dict, strict=True)

    def fit(self, parameters, config=[]):
        self.set_parameters(parameters)
        train(self.net, trainloaders[self.client_id], epochs=1)
        return self.get_parameters(), num_examples[self.client_id]["trainset"], {}

    def evaluate(self, parameters, config=[]):
        self.set_parameters(parameters)
        loss, accuracy = test(self.net, testloaders[self.client_id])
        return float(loss), num_examples[self.client_id]["testset"], float(accuracy)

    def train_valuate(self, parameters, config=[]):
        loss, accuracy = validate(self.net, trainloaders[self.client_id])
        return float(loss), num_examples[self.client_id]["trainset"], float(accuracy)

