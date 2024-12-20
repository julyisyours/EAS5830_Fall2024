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
    bsc_url = f"https://bsc-testnet.infura.io/v3/8ef000923e5f43da92da6cfbe71ccd34" # Public BSC node provider
    w3 = Web3(HTTPProvider(bsc_url))

    # Inject the Geth PoA middleware to handle Proof of Authority (PoA) consensus
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)

    # Verify the connection to the BSC network
    assert w3.is_connected(), f"Failed to connect to BSC provider at {bsc_url}"

    # Create the contract object using the ABI and contract address
    contract = w3.eth.contract(address=Web3.to_checksum_address(address), abi=abi)

    return w3, contract

if __name__ == "__main__":
    w3, contract = connect_with_middleware("contract_info.json")
    print(f"Connected to Web3: {w3.is_connected()}")
    print(f"Contract Address: {contract.address}")

