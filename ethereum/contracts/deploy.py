from web3 import Web3
from solc import compile_files

# web3.py instance
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

# compile all contract files
contracts = compile_files(['HelloWorld.sol', 'Federator.sol'])
# separate main file and link file
main_contract = contracts.pop("HelloWorld.sol:HelloWorld")
library_link = contracts.pop("Federator.sol:Federator")
