# Drain Script (SOLAR ONLY)

## Clean / New Installation
# clone repository
git clone https://github.com/galperins4/drain
cd ~/drain
# install requirements
pip3 install -r requirements.txt
# fill out config (see below)
nano ~/drain/config.ini

## Available Configuration Options 
### [Static]
| Option | Default Setting | Description | 
| :--- | :---: | :--- |
| atomic | 100000000 | atomic value - do not change |
| network | solar_mainnet | network value |
| passphrase | passphrase | 12 word delegate passphrase |
| secondphrase | None | Second 12 word delegate passphrase |
| convert_from | sxp, sxpmainnet | Network the swap is sending from - solar only |
| convert_address | addr1,addr2 | Reward address we are converting from for the swap - can support one or many|
| convert_to | usdc,xrp | Cryptocurrency we want to swap / exchange into - can support one or many |
| address_to | usdc_addr1,xrp_addr2 | Addresses to exchange into - can support one or many |
| network_to | eth,xrp | Network for the receving swap cryptocurrency - can support one or many |
| provider | provider,provider | Provider of the swap - Available options are "SimpleSwap" or "ChangeNow" |
