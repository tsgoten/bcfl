from collections import OrderedDict
import torch

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

class BCFLClient():

    def init(self, net, train, test):
        """
        Initializes the local federated client
        :param net (torch.nn.Module): the model to be trained
        :param train (func): training function on the model
        :param test (func)): test function on the model
        """
        self.net = net
        self.train = train
        self.test = test

    def get_parameters(self):
        """Get paramters of the model in a 1D array"""
        flat, indices = flatten_params(self.net.parameters())
    
    def set_parameters(self, flat_params, indices):
        """Set paramters of the model from 1D array"""
        parameters = recover_flattened(flat_params, indices, self.net)
        params_dict = zip(self.net.state_dict().keys(), parameters)
        state_dict = OrderedDict({k: torch.tensor(v) for k, v in params_dict})
        self.net.load_state_dict(state_dict, strict=True)
    
    def fit(self, paramters):
        """
        Fits the model according to the provided training function
        :param parameters: the parameters from the central model to be set
        :return: the new parameters based on training
        """
        self.set_parameters(paramters)
        self.train(self.net)
        return self.get_parameters()

    def evaluate(self, parameters=None):
        """
        Evaluates the model according to the provided test function
        :return: the test loss and accuracy
        """
        # self.set_parameters(parameters)
        loss, accuracy = self.test(self.net)
        return float(loss), float(accuracy)
