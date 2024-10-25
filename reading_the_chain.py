import random
import json
from web3 import Web3
from web3.middleware import geth_poa_middleware
from web3.providers.rpc import HTTPProvider


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
    bsc_url = f"https://bsc-testnet.infura.io/v3/8ef000923e5f43da92da6cfbe71ccd34"  # Your Infura BSC URL here
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

    After EIP-1559, there are two types of transactions:
    *Type 0* The priority fee is tx.gasPrice - block.baseFeePerGas
    *Type 2* The priority fee is min( tx.maxPriorityFeePerGas, tx.maxFeePerGas - block.baseFeePerGas )

    Conveniently, most type 2 transactions set the gasPrice field to be min( tx.maxPriorityFeePerGas + block.baseFeePerGas, tx.maxFeePerGas )
    """
    block = w3.eth.get_block(block_num, full_transactions=True)
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
    the contract to check current on-chain values.
    The provided "default_admin_role" is the correctly formatted solidity default
    admin value to use when checking with the contract.
    """
    default_admin_role = contract.functions.DEFAULT_ADMIN_ROLE().call()

    # Get the Merkle root from the contract
    onchain_root = contract.functions.merkleRoot().call()

    # Check if the admin_address has the admin role
    has_role = contract.functions.hasRole(default_admin_role, admin_address).call()

    # Get the prime owned by the owner_address
    prime = contract.functions.getPrimeByOwner(owner_address).call()

    return onchain_root, has_role, prime


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
        ordered = is_ordered_block(eth_w3, block_num)
        if ordered:
            print(f"Block {block_num} is ordered")
        else:
            print(f"Block {block_num} is not ordered")
