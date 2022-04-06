from client import CifarClient

clients = []

def initialize_clients(num_clients=3):
    for i in range(num_clients):
	    clients.append(CifarClient(i))

def train_local_clients():
	for client in clients:
		client.fit()

def evaluate_local_clients():
	for client in clients:
	    print(client.evaluate())

initialize_clients()
train_local_clients()
evaluate_local_clients()