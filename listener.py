from web3 import Web3
from web3.middleware import geth_poa_middleware
import json
import pandas as pd
from datetime import datetime

eventfile = '/home/codio/workspace/deposit_logs.csv'

def scanBlocks(chain, start_block, end_block, contract_address):
    """
    chain - string (Either 'bsc' or 'avax')
    start_block - integer first block to scan
    end_block - integer last block to scan
    contract_address - the address of the deployed contract

    This function reads "Deposit" events from the specified contract, 
    and writes information about the events to the file "deposit_logs.csv"
    """
    if chain == 'avax':
        api_url = "https://api.avax-test.network/ext/bc/C/rpc"  # AVAX C-chain testnet
    elif chain == 'bsc':
        api_url = "https://data-seed-prebsc-1-s1.binance.org:8545/"  # BSC testnet
    else:
        raise ValueError("Invalid chain specified. Choose 'avax' or 'bsc'.")

    w3 = Web3(Web3.HTTPProvider(api_url))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)

    # Define the Deposit ABI
    DEPOSIT_ABI = json.loads('[{"anonymous": false, "inputs": [{"indexed": true, "internalType": "address", "name": "token", "type": "address"}, {"indexed": true, "internalType": "address", "name": "recipient", "type": "address"}, {"indexed": false, "internalType": "uint256", "name": "amount", "type": "uint256"}], "name": "Deposit", "type": "event"}]')
    contract = w3.eth.contract(address=contract_address, abi=DEPOSIT_ABI)

    all_events = []

    # Adjust block range
    if end_block - start_block < 30:
        # Fetch events for a small block range
        event_filter = contract.events.Deposit.create_filter(fromBlock=start_block, toBlock=end_block)
        events = event_filter.get_all_entries()
        all_events.extend(events)
    else:
        # Loop through each block in the range to avoid timeouts
        for block_num in range(start_block, end_block + 1):
            event_filter = contract.events.Deposit.create_filter(fromBlock=block_num, toBlock=block_num)
            events = event_filter.get_all_entries()
            all_events.extend(events)

    # Process events and save to CSV
    deposit_data = []
    for evt in all_events:
        data = {
            'chain': chain,
            'token': evt.args['token'],
            'recipient': evt.args['recipient'],
            'amount': evt.args['amount'],
            'transactionHash': evt.transactionHash.hex(),
            'address': evt.address,
            'date': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        }
        deposit_data.append(data)

    # Write to CSV file
    df = pd.DataFrame(deposit_data)
    df.to_csv(eventfile, mode='a', header=not pd.read_csv(eventfile, nrows=1).empty, index=False)
