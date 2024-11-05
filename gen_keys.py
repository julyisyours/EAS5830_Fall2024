from web3 import Web3
import eth_account
import os

def get_keys(challenge, keyId=0, filename="eth_mnemonic.txt"):
    """
    Generate a stable private key
    challenge - byte string
    keyId (integer) - which key to use
    filename - filename to read and store mnemonics

    Each mnemonic is stored on a separate line
    If fewer than (keyId+1) mnemonics have been generated, generate a new one and return that
    """

    # Initialize Web3 instance
    w3 = Web3()

    # Read the mnemonic from the file or use the provided one
    try:
        with open(filename, 'r') as f:
            mnemonics = f.readlines()
        
        # Get the specific mnemonic based on keyId
        if keyId < len(mnemonics):
            mnemonic = mnemonics[keyId].strip()
        else:
            raise ValueError("Mnemonic for keyId not found in file.")
    except FileNotFoundError:
        raise FileNotFoundError(f"Mnemonic file '{filename}' not found. Make sure the file is in the correct directory.")

    # Enable unaudited HD wallet features for account generation
    w3.eth.account.enable_unaudited_hdwallet_features()

    # Generate the account based on mnemonic and keyId using a specific HD path
    acct = w3.eth.account.from_mnemonic(mnemonic, account_path=f"m/44'/60'/0'/0/{keyId}")

    # Encode the challenge as a message
    msg = eth_account.messages.encode_defunct(challenge)

    # Sign the message with the generated account
    signature = acct.sign_message(msg).signature

    # Return the signature (as HexBytes) and Ethereum address of the account
    return signature, acct.address

if __name__ == "__main__":
    for i in range(4):
        challenge = os.urandom(64)
        sig, addr = get_keys(challenge=challenge, keyId=i)
        print(f"Address: {addr}")
        print(f"Signature: {sig.hex()}")

