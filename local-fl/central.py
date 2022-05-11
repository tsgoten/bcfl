from client import CifarClient, NUM_CLIENTS, Net
import random
import torch

NUM_EPOCHS = 1000
clients = []

global_client = CifarClient(-1)

def initialize_clients(num_clients=3):
    for i in range(num_clients):
	    clients.append(CifarClient(i))

def evaluate_local_clients():
	for client in clients:
	    print(client.evaluate(global_client.get_parameters()))

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
		torch.save(global_client.net.state_dict(), "./models/global_dict_{}.pth".format(epoch))
		torch.save(global_client.net, "./models/global_model_{}.pth".format(epoch))
