from client import CifarClient, NUM_CLIENTS, Net
import random
import torch

import wandb

NUM_EPOCHS = 1000
clients = []

global_client = CifarClient(-1)
wandb.init(project="bcfl", entity="tarang")

def initialize_clients(num_clients=3):
    for i in range(num_clients):
        clients.append(CifarClient(i))


def evaluate_local_clients():
    metrics = {}
    for client in clients:
        test_loss, _, test_acc = client.evaluate(global_client.get_parameters())
        train_loss, _, train_acc = client.train_valuate(global_client.get_parameters())
        metrics["Agent_{}/test_loss".format(client.client_id)] = test_loss 
        metrics["Agent_{}/train_loss".format(client.client_id)] = train_loss 
        metrics["Agent_{}/train_accuracy".format(client.client_id)] = train_acc
        metrics["Agent_{}/test_accuracy".format(client.client_id)] = test_acc
        print("Test Acc: {}, Train Acc: {}".format(test_acc, train_acc))
    wandb.log(metrics)



def train_local_clients():
    for client in clients:
        client.fit(global_client.get_parameters())


def aggregate_local_clients():
    params = None
    for client in clients:
        client_params = client.get_parameters()
        if params is None:
            params = [cparam / len(clients) for cparam in client_params]
        else:
            for param, cparam in zip(params, client_params):
                param += cparam / len(clients)
        # print("CLIENT PARAMS", client_params)
    global_client.set_parameters(params)


initialize_clients(NUM_CLIENTS)
for epoch in range(NUM_EPOCHS):
    print("******** Epoch: {}".format(epoch))
    evaluate_local_clients()
    train_local_clients()
    aggregate_local_clients()
    if epoch % 40 == 0:
        torch.save(global_client.net.state_dict(),
                   "./models/global_dict_{}.pth".format(epoch))
        torch.save(global_client.net,
                   "./models/global_model_{}.pth".format(epoch))
