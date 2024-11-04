import eth_account
from eth_account.messages import encode_defunct

def sign(m):
    # Step 1: Create a new Ethereum account
    account = eth_account.Account.create()
    eth_address = account.address
    private_key = account.key
    
    print("Generated address:", eth_address)
    print("Private key:", private_key.hex())
    
    # Step 2: Prepare the message
    try:
        message = encode_defunct(text=m)
    except Exception as e:
        print("Error encoding message:", e)
        return None, None

    # Step 3: Sign the message
    try:
        signed_message = account.sign_message(message)
    except Exception as e:
        print("Error signing message:", e)
        return None, None

    # Ensure signed_message is a SignedMessage instance
    assert isinstance(signed_message, eth_account.datastructures.SignedMessage)
    
    print("Signed message:", signed_message)
    
    return eth_address, signed_message
