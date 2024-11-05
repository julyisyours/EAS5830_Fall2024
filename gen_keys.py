from web3 import Web3
import eth_account
import os

def get_keys(challenge, keyId=0, filename="eth_mnemonic.txt"):
    w3 = Web3()

    try:
        with open(filename, 'r') as f:
            mnemonics = f.readlines()
        if keyId < len(mnemonics):
            mnemonic = mnemonics[keyId].strip()
        else:
            raise ValueError("Mnemonic for keyId not found in file.")
    except FileNotFoundError:
        raise FileNotFoundError(f"Mnemonic file '{filename}' not found. Please check the location.")

    w3.eth.account.enable_unaudited_hdwallet_features()
    acct = w3.eth.account.from_mnemonic(mnemonic, account_path=f"m/44'/60'/0'/0/{keyId}")
    eth_addr = acct.address

    msg = eth_account.messages.encode_defunct(challenge)
    sig = acct.sign_message(msg)

    recovered_address = eth_account.Account.recover_message(msg, signature=sig.signature)
    assert recovered_address == eth_addr, "Failed to sign message properly"

    return sig, eth_addr

if __name__ == "__main__":
    for i in range(4):
        challenge = os.urandom(64)
        sig, addr = get_keys(challenge=challenge, keyId=i)
        print(addr)

