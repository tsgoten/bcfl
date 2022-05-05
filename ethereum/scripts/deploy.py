# Deployment Script for local ganache network

from web3 import Web3
from solc import compile_files

# web3.py instance
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

contract_folder = '../contracts/'
contracts = ['HelloWorld.sol', 'Federator.sol']
contract_paths = [contract_folder + x for x in contracts]

# compile all contract files
contracts = compile_files(contract_paths)

# separate main file and link file
main_contract = contracts.pop(contract_paths[0] + ":HelloWorld")
library_link = contracts.pop(contract_paths[1] + ":Federator")

def deploy_contract(contract_interface):
    # Instantiate and deploy contract
    abi = contract_interface['abi']
    contract = w3.eth.contract(
        abi=abi,
        bytecode=contract_interface['bin']
    )
    # Get transaction hash from deployed contract
    tx_hash = contract.constructor('Test Message').transact({
        'from': w3.eth.accounts[1], 
        'gas': 410000
    })
    
    # Get tx receipt to get contract address
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return tx_receipt['contractAddress'], abi

contract_address, abi = deploy_contract(main_contract)
print('Deployed at: ', contract_address)
print('abi: ', abi)


