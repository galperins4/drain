from client import ArkClient
from configparser import ConfigParser
from pathlib import Path
from modules.exchange import Exchange
from crypto.transactions.builder.transfer import Transfer
from crypto.configuration.network import set_custom_network
from datetime import datetime


def get_config():
    home = str(Path.home())
    config_path = home+'/drain/config.ini'
    config = ConfigParser()
    config.read(config_path)

    config_dict = {'atomic' : int(config.get('static', 'atomic')),
                   'test' : config.get('static', 'test'),
                   'network' : config.get('static', 'network'),
                   'passphrase' : config.get('static', 'passphrase'),
                   'secondphrase' : config.get('static', 'secondphrase'),
                   'convert_from' : config.get('static', 'convert_from'),
                   'convert_address' : config.get('static', 'convert_address'),
                   'convert_to' : config.get('static', 'convert_to'),
                   'address_to' : config.get('static', 'address_to'),
                   'network_to' : config.get('static', 'network_to'),
                   'provider' : config.get('static', 'provider'),
                   'fixed' : config.get('static', 'fixed'),
                   'fixed_amt' : int(config.get('static', 'fixed_amt'))}

    return config_dict


def build_transfer_tx(config, exchange, fee, amt, n):
    #transaction = Transfer()
    #transaction.set_fee(fee)
    #transaction.set_nonce(n+1)
    net_exchange = amt-fee

    # exchange processing
    pay_in = exchange.exchange_select(config['convert_address'], net_exchange, config['provider'])
    if pay_in == config['convert_address']:
        print('Failed Exchange - Quit Processing')
        quit()
    else:
        print('Succcessful Exchange')

    #transaction.add_transfer(net_exchange, pay_in)
    transaction = Transfer(recipientId=pay_in, amount=net_exchange, vendorField="drain", fee=fee)
    transaction.set_nonce(n+1)
    transaction.schnorr_sign(config['passphrase'])
    
    #transaction.sign(config['passphrase'])
    sp = config['secondphrase']
    if sp == 'None':
        sp = None
    if sp is not None:
        transaction.second_sign(sp)

    transaction_dict = transaction.to_dict()
    return transaction_dict


def get_client(ip="localhost"):
    ark_epoch = ["2017","3","21","13","00","00"]
    t = [int(i) for i in ark_epoch]
    epoch = datetime(t[0], t[1], t[2], t[3], t[4], t[5])
    version = 23
    wif = 170
    set_custom_network(epoch, version, wif)
    return ArkClient('http://{0}:{1}/api'.format(ip, 4003))


def get_fee(client, numtx=1):
    node_configs = self.client.node.configuration()['data']['transactionPool']['dynamicFees']
    if node_configs['enabled'] == "False":
        transaction_fee = int(0.1 * self.config.atomic)
    else:
        dynamic_offset = node_configs['addonBytes']['transfer']
        fee_multiplier = node_configs['minFeePool']
        standard_tx = 230
        message = "drain"
        v_msg = len(message) 
        tx_size = standard_tx + v_msg
        
        #calculate transaction fee
        transaction_fee = int((dynamic_offset+tx_size)*fee_multiplier)
    '''
    node_configs = client.node.configuration()['data']['pool']['dynamicFees']
    dynamic_offset = node_configs['addonBytes']['transfer']
    fee_multiplier = node_configs['minFeePool']
    sp = config['secondphrase']

    # get size of transaction
    multi_tx = 125
    if sp == 'None':
        second_sig = 0
    else:
        second_sig = 64
    per_tx_fee = 29
    tx_size = multi_tx + second_sig + (numtx * per_tx_fee)

    # calculate transaction fee
    transaction_fee = int((dynamic_offset + (round(tx_size/2) + 1)) * fee_multiplier)
    '''
    return transaction_fee


if __name__ == '__main__':
    # get client / config / fees
    config = get_config()
    client = get_client()
    fee = get_fee(client)
    exchange = Exchange(config)

    if config['test'] == 'Y':
        print("Testing Config")
        # exchange processing
        pay_in = exchange.exchange_select(config['convert_address'], 750*config['atomic'], config['provider'])
        if pay_in == config['convert_address']:
            print('Failed Exchange')
        else:
            print('Succcessful Exchange')
        quit()
    
    # get wallet balance
    wallet = client.wallets.get(config['convert_address'])['data']
    nonce = int(wallet['nonce'])
    wallet_balance = int(wallet['balance'])

    # check for fixed processing
    if config['fixed'] == 'Y':
        amount = config['fixed_amt'] * config['atomic'] + fee
        check = wallet_balance - amount
        # check to see if there is enough in wallet to pay fixed amount
        if check < 0:
            print('wallet does not have sufficient balance, draining remaining funds')
            balance = wallet_balance
        else:
            print('wallet has enough funds, converting fixed amount')
            balance = amount
    else:
        # drain full balance
        balance = wallet_balance

    # build transfer
    tx = build_transfer_tx(config, exchange, fee, balance, nonce)
    print(tx)

    # broadcast transaction
    transaction = client.transactions.create([tx])
    print(transaction)
