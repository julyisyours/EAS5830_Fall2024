from web3 import Web3
from eth_account.messages import encode_defunct
from web3.middleware import geth_poa_middleware
import json
import secrets
import random

# Set up web3 connection
w3 = Web3(Web3.HTTPProvider("https://api.avax-test.network/ext/bc/C/rpc"))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

# Load the ABI from the NFT.abi file
with open("NFT.abi", "r") as abi_file:
    abi = json.load(abi_file)
    
# Contract address
contract_address = "0x85ac2e065d4526FBeE6a2253389669a12318A412"
# print("Contract address:", contract_address)
contract = w3.eth.contract(address=contract_address, abi=abi)

# Verify the presence of the claim function
# for function_abi in abi:
#     if function_abi.get("name") == "claim":
#         print("ABI for claim function:", function_abi)

# print("All contract functions:", contract.all_functions())

my_address = "0xAe693a9b03B2Ef5F642f82d910e19D7b47Bb87B7"
my_private_key = "0xfb91cee50e8cbcbb250f17a85ca66b0f8b915cf27764aeccce611915ae022caf"

# Generate a random 32-byte nonce
nonce = secrets.token_bytes(32)
print("Nonce (bytes32):", nonce)

# Attempt to build and sign the transaction
try:
    # Directly call the claim function with transact
    txn_hash = contract.functions.claim(my_address, nonce).transact({
        'from': my_address,
        'gas': 200000,  # Increased gas limit
        'gasPrice': w3.toWei('30', 'gwei')
    })
    
    # Wait for transaction confirmation
    receipt = w3.eth.wait_for_transaction_receipt(txn_hash)
    print("Transaction receipt:", receipt)
    
except Exception as e:
    print("Error during transaction:", e)

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

