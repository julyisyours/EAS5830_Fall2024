from web3 import Web3
from eth_account.messages import encode_defunct
from web3.middleware import geth_poa_middleware
import json
import os
import secrets
import random

# Set up web3 connection
w3 = Web3(Web3.HTTPProvider("https://api.avax-test.network/ext/bc/C/rpc"))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

# Load the ABI from the NFT.abi file
with open("NFT.abi", "r") as abi_file:
    abi = json.load(abi_file)
    
# Contract address and ABI (assume ABI is available)
contract_address = "0x85ac2e065d4526FBeE6a2253389669a12318A412"

# Set up the contract
contract = w3.eth.contract(address=contract_address, abi=abi)

my_address = "0x52E97A5Da00a35471D3d2e78dF9104eB0b2Ae38D"
my_private_key = "0xe3704c89c1b265597e5f11316f1d7a225487254b220441b37d87f34b0fe2df75"

# Generate a random 32-byte nonce
nonce = secrets.token_bytes(32)

# Build the transaction to call the claim function
transaction = contract.functions.claim(my_address, nonce).buildTransaction({
    'from': my_address,
    'gas': 2000,
    'gasPrice': w3.toWei('30', 'gwei'),
    'nonce': w3.eth.get_transaction_count(my_address),
})

# Sign and send the transaction
signed_txn = w3.eth.account.sign_transaction(transaction, private_key = my_private_key)
txn_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)

# Wait for transaction confirmation
receipt = w3.eth.wait_for_transaction_receipt(txn_hash)
print("Transaction receipt:", receipt)

def signChallenge( challenge ):

    w3 = Web3()

    #This is the only line you need to modify
    sk = my_private_key 

    acct = w3.eth.account.from_key(sk)

    signed_message = w3.eth.account.sign_message( challenge, private_key = acct._private_key )

    return acct.address, signed_message.signature


def verifySig():
    """
        This is essentially the code that the autograder will use to test signChallenge
        We've added it here for testing 
    """

    challenge_bytes = random.randbytes(32)

    challenge = encode_defunct(challenge_bytes)
    address, sig = signChallenge( challenge )

    w3 = Web3()

    return w3.eth.account.recover_message( challenge , signature=sig ) == address

if __name__ == '__main__':
    """
        Test your function
    """
    if verifySig():
        print( f"You passed the challenge!" )
    else:
        print( f"You failed the challenge!" )
