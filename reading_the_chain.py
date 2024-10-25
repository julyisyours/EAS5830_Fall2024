import random
import json
from web3 import Web3
from web3.middleware import geth_poa_middleware
from web3.providers.rpc import HTTPProvider


# If you use one of the suggested infrastructure providers, the url will be of the form
# now_url  = f"https://eth.nownodes.io/{now_token}"
# alchemy_url = f"https://eth-mainnet.alchemyapi.io/v2/{alchemy_token}"
# infura_url = f"https://mainnet.infura.io/v3/{infura_token}"

def connect_to_eth():
    url = f"https://mainnet.infura.io/v3/8ef000923e5f43da92da6cfbe71ccd34"  # Your Infura URL here
    w3 = Web3(HTTPProvider(url))
    assert w3.is_connected(), f"Failed to connect to provider at {url}"
    return w3

def connect_with_middleware(contract_json):
    # Read contract address and ABI from the JSON file
    with open(contract_json, "r") as f:
        d = json.load(f)
        d = d['bsc']
        address = d['address']
        abi = d['abi']

    # Connect to Binance Smart Chain (BSC) using the correct provider URL
    bsc_url = f"https://bsc-testnet.infura.io/v3/8ef000923e5f43da92da6cfbe71ccd34" # Your Infura BSC URL here
    w3 = Web3(HTTPProvider(bsc_url))

    # Inject the Geth PoA middleware to handle Proof of Authority (PoA) consensus
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)

    # Verify the connection to the BSC network
    assert w3.is_connected(), f"Failed to connect to BSC provider at {bsc_url}"

    # Create the contract object using the ABI and contract address
    contract = w3.eth.contract(address=Web3.to_checksum_address(address), abi=abi)

    return w3, contract


def is_ordered_block(w3, block_num):
	"""
	Takes a block number
	Returns a boolean that tells whether all the transactions in the block are ordered by priority fee

	Before EIP-1559, a block is ordered if and only if all transactions are sorted in decreasing order of the gasPrice field

	After EIP-1559, there are two types of transactions
		*Type 0* The priority fee is tx.gasPrice - block.baseFeePerGas
		*Type 2* The priority fee is min( tx.maxPriorityFeePerGas, tx.maxFeePerGas - block.baseFeePerGas )

	Conveniently, most type 2 transactions set the gasPrice field to be min( tx.maxPriorityFeePerGas + block.baseFeePerGas, tx.maxFeePerGas )
	"""
	block = w3.eth.get_block(block_num)
	# ordered = False
	# return ordered
	base_fee = block.get('baseFeePerGas', None)  # EIP-1559 blocks will have this, others will not.

  # List to store calculated priority fees for each transaction
  priority_fees = []

  for tx in block.transactions:
      if tx.type == '0x0':  # Type 0 transaction (pre-EIP-1559)
          # Priority fee = gasPrice - baseFeePerGas if baseFeePerGas exists, otherwise just gasPrice
          if base_fee:
              priority_fee = tx.gasPrice - base_fee
          else:
              priority_fee = tx.gasPrice
      elif tx.type == '0x2':  # Type 2 transaction (post-EIP-1559)
          # Priority fee = min( maxPriorityFeePerGas, maxFeePerGas - baseFeePerGas )
          priority_fee = min(tx.maxPriorityFeePerGas, tx.maxFeePerGas - base_fee)
      else:
          # For simplicity, assume other types are handled similarly to Type 0 (unlikely)
          priority_fee = tx.gasPrice

        # Add the priority fee to the list
      priority_fees.append(priority_fee)

  # Check if the priority fees are in descending order
  return priority_fees == sorted(priority_fees, reverse=True)

def get_contract_values(contract, admin_address, owner_address):
	"""
	Takes a contract object, and two addresses (as strings) to be used for calling
	the contract to check current on chain values.
	The provided "default_admin_role" is the correctly formatted solidity default
	admin value to use when checking with the contract
	To complete this method you need to make three calls to the contract to get:
	  onchain_root: Get and return the merkleRoot from the provided contract
	  has_role: Verify that the address "admin_address" has the role "default_admin_role" return True/False
	  prime: Call the contract to get and return the prime owned by "owner_address"

	check on available contract functions and transactions on the block explorer at
	https://testnet.bscscan.com/address/0xaA7CAaDA823300D18D3c43f65569a47e78220073
	"""
	default_admin_role = int.to_bytes(0, 32, byteorder="big")
  # default_admin_role = contract.functions.DEFAULT_ADMIN_ROLE().call()
	# TODO complete the following lines by performing contract calls
	onchain_root = contract.functions.merkleRoot().call()
	# Get and return the merkleRoot from the provided contract
	has_role = contract.functions.hasRole(default_admin_role, admin_address).call()
	# Check the contract to see if the address "admin_address" has the role "default_admin_role"
	prime = contract.functions.getPrimeByOwner(owner_address).call()

	# Call the contract to get the prime owned by "owner_address"

	return onchain_root, has_role, prime


"""
	This might be useful for testing (main is not run by the grader feel free to change 
	this code anyway that is helpful)
"""
if __name__ == "__main__":
	# These are addresses associated with the Merkle contract (check on contract
	# functions and transactions on the block explorer at
	# https://testnet.bscscan.com/address/0xaA7CAaDA823300D18D3c43f65569a47e78220073
	admin_address = "0xAC55e7d73A792fE1A9e051BDF4A010c33962809A"
	owner_address = "0x793A37a85964D96ACD6368777c7C7050F05b11dE"
	contract_file = "contract_info.json"

	eth_w3 = connect_to_eth()
	cont_w3, contract = connect_with_middleware(contract_file)

	latest_block = eth_w3.eth.get_block_number()
	london_hard_fork_block_num = 12965000
	assert latest_block > london_hard_fork_block_num, f"Error: the chain never got past the London Hard Fork"

	n = 5
	for _ in range(n):
		block_num = random.randint(1, london_hard_fork_block_num - 1)
		ordered = is_ordered_block(block_num)
		if ordered:
			print(f"Block {block_num} is ordered")
		else:
			print(f"Block {block_num} is not ordered")
