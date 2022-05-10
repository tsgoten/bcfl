import torch
import torch.nn as nn

from collections import OrderedDict


class Net(nn.Module):
	def __init__(self):
		super(Net, self).__init__()
		self.conv1 = nn.Conv2d(3, 6, 5)
		self.pool = nn.MaxPool2d(2, 2)
		self.conv2 = nn.Conv2d(6, 16, 5)
		self.fc1 = nn.Linear(16 * 5 * 5, 120)
		self.fc2 = nn.Linear(120, 84)
		self.fc3 = nn.Linear(84, 10)

	def forward(self, x):
		x = self.pool(F.relu(self.conv1(x)))
		x = self.pool(F.relu(self.conv2(x)))
		x = x.view(-1, 16 * 5 * 5)
		x = F.relu(self.fc1(x))
		x = F.relu(self.fc2(x))
		x = self.fc3(x)
		return x

	def set_parameters(self, parameters):
			params_dict = zip(self.state_dict().keys(), parameters)
			state_dict = OrderedDict({k: torch.tensor(v) for k, v in params_dict})
			self.load_state_dict(state_dict, strict=True)

# def flatten(net):
# 	# Print model's state_dict
# 	flattened = []
# 	shape = []
# 	print("Model's state_dict:")
# 	for param_tensor in net.state_dict():
# 		layer_shape = net.state_dict()[param_tensor].size()
# 		print(param_tensor, "\t", shape)
# 		flattened += torch.flatten(net.state_dict()[param_tensor])
# 		shape.append(list(layer_shape))
# 	out = [i.item() for i in flattened]
# 	return out, shape

# def unflatten(out, shape):
# 	unflatten = nn.Unflatten(1, shape)
# 	net = unflatten(torch.tensor(out))
# 	print("Unflat Model's state_dict:")
# 	for param_tensor in net.state_dict():
# 		layer_shape = net.state_dict()[param_tensor].size()
# 		print(param_tensor, "\t", shape)

def flatten_params(parameters):
	"""
	flattens all parameters into a single column vector. Returns the dictionary to recover them
	:param: parameters: a generator or list of all the parameters
	:return: a dictionary: {"params": [#params, 1],
	"indices": [(start index, end index) for each param] **Note end index in uninclusive**

	"""
	l = [torch.flatten(p) for p in parameters]
	indices = []
	s = 0
	for p in l:
			size = p.shape[0]
			indices.append((s, s+size))
			s += size
	flat = torch.cat(l).view(-1, 1)
	flat_floats = [i.item() for i in flat]
	return flat_floats, indices


def recover_flattened(flat_params, indices, model):
	"""
	Gives a list of recovered parameters from their flattened form
	:param flat_params: [#params, 1]
	:param indices: a list detaling the start and end index of each param [(start, end) for param]
	:param model: the model that gives the params with correct shapes
	:return: the params, reshaped to the ones in the model, with the same order as those in the model
	"""
	flat_params = torch.tensor(flat_params)
	l = [flat_params[s:e] for (s, e) in indices]
	for i, p in enumerate(model.parameters()):
		l[i] = l[i].view(*p.shape)
	return l


net = Net()
print(net)
out, indices = flatten_params(net.parameters())
new_params = recover_flattened(out, indices, net)

new_net = Net()
new_net.set_parameters(new_params)
print(new_net)