## Common
1. Create a VENV folder
	- `python3 -m venv venv`
2. Activate the VENV
	- `source ./venv/bin/activate`
3. Install requirements.txt
	- `pip3 install -r requirements.txt`

## Run Script
1. Go to script.py
2. Set `RPC_URL` to the RPC you want to query
2. Set `CONTRACT_ADDRESS` to the appropriate UNSRegistry contract address for the RPC (See [UNS Config](https://github.com/unstoppabledomains/uns/blob/main/uns-config.json))
2. Set `TLD` to the TLD you want to filter for
2. Set `BLOCKS` to the number of blocks to search through
3. Run the script
	- `python3 script.py` 