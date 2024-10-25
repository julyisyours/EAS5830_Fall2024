from web3 import Web3
from web3.contract import Contract
from web3.providers.rpc import HTTPProvider
import requests
import json

# Bored Ape contract address
bayc_address = "0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D"

# Connect to an Ethereum node
api_url = f"https://mainnet.infura.io/v3/8ef000923e5f43da92da6cfbe71ccd34"  # Replace with your Ethereum node URL
provider = HTTPProvider(api_url)
web3 = Web3(provider)

# Convert the Bored Ape contract address to checksum format
contract_address = web3.toChecksumAddress(bayc_address)

# Load the ABI from the file 'abi.json'
with open('/home/codio/workspace/abi.json', 'r') as f:
    abi = json.load(f)

# Connect to the contract
contract = web3.eth.contract(address=contract_address, abi=abi)

def get_ape_info(apeID):
    assert isinstance(apeID, int), f"{apeID} is not an int"
    assert 0 <= apeID < 10000, f"{apeID} must be between 0 and 9999"

    data = {'owner': "", 'image': "", 'eyes': ""}

    try:
        # Get the current owner of the ape
        owner = contract.functions.ownerOf(apeID).call()
        data['owner'] = owner

        # Get the token URI for the ape
        token_uri = contract.functions.tokenURI(apeID).call()

        # Replace 'ipfs://' with an IPFS gateway URL to fetch metadata from IPFS
        ipfs_url = token_uri.replace("ipfs://", "https://ipfs.io/ipfs/")

        # Retrieve metadata from IPFS
        response = requests.get(ipfs_url)
        metadata = response.json()

        # Extract image URI and eyes attribute
        data['image'] = metadata['image']  # This will be an IPFS URI
        # Find the attribute with "trait_type" as "Eyes"
        eyes_attribute = next(attr['value'] for attr in metadata['attributes'] if attr['trait_type'] == 'Eyes')
        data['eyes'] = eyes_attribute

    except Exception as e:
        print(f"Error retrieving Ape info for Ape ID {apeID}: {e}")

    # Validation
    assert isinstance(data, dict), f'get_ape_info({apeID}) should return a dict'
    assert all([key in data.keys() for key in ['owner', 'image', 'eyes']]), \
        "Return value should include the keys 'owner', 'image', and 'eyes'"

    return data

# Example usage
if __name__ == "__main__":
    ape_id = 1  # Replace with the desired Ape ID
    ape_info = get_ape_info(ape_id)
    print(ape_info)

