# Testing script for local ganache network

from web3 import Web3
from solc import compile_files

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
contract_addr = '0xF83ab3D91Ab7Dc0Df93c5692D2E844f902aAE692'
abi = [{'constant': False, 'inputs': [{'name': 'newMessage', 'type': 'string'}], 'name': 'update', 'outputs': [], 'payable': False, 'stateMutability': 'nonpayable', 'type': 'function'}, {'constant': True, 'inputs': [], 'name': 'message', 'outputs': [{'name': '', 'type': 'string'}], 'payable': False, 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'name': 'initMessage', 'type': 'string'}], 'payable': False, 'stateMutability': 'nonpayable', 'type': 'constructor'}]

contract = w3.eth.contract(
    address=contract_addr,
    abi=abi
)

print(contract.functions.message().call())
