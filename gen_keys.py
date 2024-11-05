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

    # Step 1: Read the mnemonic from file
    try:
        with open(filename, 'r') as f:
            mnemonics = f.readlines()

        # Select the mnemonic for the given keyId
        if keyId < len(mnemonics):
            mnemonic = mnemonics[keyId].strip()
        else:
            raise ValueError("Mnemonic for keyId not found in file.")
    except FileNotFoundError:
        raise FileNotFoundError(f"Mnemonic file '{filename}' not found. Please check the location.")

    # Step 2: Enable HD wallet features for account derivation
    w3.eth.account.enable_unaudited_hdwallet_features()

    # Step 3: Create account from mnemonic using a specific path for keyId
    acct = w3.eth.account.from_mnemonic(mnemonic, account_path=f"m/44'/60'/0'/0/{keyId}")
    eth_addr = acct.address  # The Ethereum address derived from the account

    # Step 4: Sign the challenge message
    msg = eth_account.messages.encode_defunct(challenge)
    sig = acct.sign_message(msg)  # `sig` contains the signature object with .signature

    # Step 5: Verify the signature to ensure correctness
    recovered_address = eth_account.Account.recover_message(msg, signature=sig.signature)
    assert recovered_address == eth_addr, "Failed to sign message properly"

    # Return the signature and address
    return sig.signature, eth_addr

if __name__ == "__main__":
    for i in range(4):
        challenge = os.urandom(64)
        sig, addr = get_keys(challenge=challenge, keyId=i)
        print(addr)

