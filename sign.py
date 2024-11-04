import eth_account
from web3 import Web3
from eth_account.messages import encode_defunct


def sign(m):
    w3 = Web3()
    
    # Step 1: Create a new Ethereum account
    account = eth_account.Account.create()
    eth_address = account.address
    private_key = account.key  # private_key can be used to sign the message

    # Step 2: Prepare the message
    message = encode_defunct(text=m)  # Encoding the message

    # Step 3: Sign the message with the private key
    signed_message = account.sign_message(message)

    # generate signature
    # your code here

    signed_message = None

    assert isinstance(signed_message, eth_account.datastructures.SignedMessage)

    return eth_address, signed_message
