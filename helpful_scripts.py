from brownie import (
    network,
    accounts,
    config,
    Wei
)

from decimal import *

def get_account(index=None, id=None):
    if index:
        return accounts[index]
    #if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
    #    return accounts[0]
    if id:
        return accounts.load(id)
    if network.show_active() in config["networks"]:
        return accounts.add(config["wallets"]["from_key"])
    return None

# expects input as float of ether, returns value in ethers
def amount_in_wei(_amount):
    return Wei(f"{round(_amount,4)} ether")

def amount_in_eths(_amount):
    return Wei(_amount).to("ether").quantize(Decimal('1.000'))

def account_in_eths(_account):
    return (amount_in_eths(get_account(_account).balance()))

def eths_r_equal(_amount1,_amount2):
    return amount_in_eths(_amount1) == amount_in_eths(_amount2)

