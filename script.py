from web3 import Web3
from datetime import datetime
import time

def fetch_newuri_events_paginated(w3, CONTRACT_ADDRESS, NEW_URI_SIGNATURE, TLD, from_block, to_block, batch_size=1000):
    all_events = []
    current_from_block = from_block
    
    while current_from_block <= to_block:
        current_to_block = min(current_from_block + batch_size - 1, to_block)
        
        try:
            print(f"Fetching blocks {current_from_block} to {current_to_block}...")
            
            logs = w3.eth.get_logs({
                'address': Web3.to_checksum_address(CONTRACT_ADDRESS),
                'topics': [NEW_URI_SIGNATURE],
                'fromBlock': current_from_block,
                'toBlock': current_to_block
            })
            
            for log in logs:
                try:
                    # Convert HexBytes to regular bytes
                    data = log['data']
                    if isinstance(data, (bytes, bytearray)):
                        data = data.hex()
                    if data.startswith('0x'):
                        data = data[2:]
                    
                    # Convert hex string to bytes
                    data_bytes = bytes.fromhex(data)
                    
                    # Decode the string data
                    uri_length = int.from_bytes(data_bytes[32:64], 'big')
                    uri = data_bytes[64:64+uri_length].decode('utf-8')
                    
                    # Filter for URIs containing '.' and ending with 'TLD'
                    if '.' in uri and uri.endswith(TLD):
                        token_id = int(log['topics'][1].hex(), 16)
                        
                        all_events.append({
                            'tokenId': token_id,
                            'uri': uri,
                            'blockNumber': log['blockNumber'],
                            'transactionHash': log['transactionHash'].hex(),
                            'timestamp': datetime.fromtimestamp(
                                w3.eth.get_block(log['blockNumber'])['timestamp']
                            ).strftime('%Y-%m-%d %H:%M:%S')
                        })
                except Exception as e:
                    print(f"Error processing log: {e}")
                    continue
            
            # Add a small delay between requests to be RPC-friendly
            time.sleep(0.1)
            
        except Exception as e:
            print(f"Error fetching batch {current_from_block}-{current_to_block}: {str(e)}")
            # Reduce batch size on error
            batch_size = max(batch_size // 2, 100)
            print(f"Reducing batch size tos {batch_size}")
            time.sleep(1)  # Wait longer on error
            continue
        
        current_from_block = current_to_block + 1
    
    return all_events

def main():
    
    RPC_URL = "https://mainnet.base.org" # Connect to blockchain
    CONTRACT_ADDRESS = "0xF6c1b83977DE3dEffC476f5048A0a84d3375d498" # UNS Registry contract address for chain. 
    # See https://github.com/unstoppabledomains/uns/blob/main/uns-config.json 
    TLD = ".u" # Top-level domain to filter for
    BLOCKS = 10000 # Number of blocks to fetch
    
    try:
        w3 = Web3(Web3.HTTPProvider(RPC_URL))
        if not w3.is_connected():
            raise Exception("Failed to connect to BASE chain")
        
        # Calculate NewURI event signature and ensure it has 0x prefix
        event_signature = w3.keccak(text="NewURI(uint256,string)")
        NEW_URI_SIGNATURE = '0x' + event_signature.hex() if not event_signature.hex().startswith('0x') else event_signature.hex()
            
        current_block = w3.eth.block_number
        from_block = current_block - BLOCKS
        
        print(f"Connected to BASE chain at block {current_block}")
        print(f"Event signature: {NEW_URI_SIGNATURE}")
        print(f"Fetching NewURI events from block {from_block} to {current_block}")
        
        events = fetch_newuri_events_paginated(w3, CONTRACT_ADDRESS, NEW_URI_SIGNATURE, TLD, from_block, current_block)
        print(f"\nFound {len(events)} matching events:")
        
        for event in events:
            print(f"\nToken ID: {event['tokenId']}")
            print(f"URI: {event['uri']}")
            print(f"Block: {event['blockNumber']}")
            print(f"Transaction: {event['transactionHash']}")
            print(f"Timestamp: {event['timestamp']}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()