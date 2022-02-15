import pytest
import brownie

from decimal import *
from brownie import network, Scissors, Wei 
from scripts.helpful_scripts import get_account
from scripts.helpful_tests import create_contract,init_presales,finish_presales, whitelist, setMaxDrop

# Set the test environment at module level for all tests below
@pytest.fixture(scope="module", autouse=True)
def contract():
    return create_contract()

# After setting up module baseline (previous function) for fixtures
# we define the isolation level of the fixture for function (ie every test 
# function will keep previous status setup at module level as the baseline) 
@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass

# Let us validate if we can mint one NFT during public sales 
#@pytest.mark.skip(reason="focus")  
def test_can_mint_scissor_public_sales(contract):
    if network.show_active() not in ["development"] or "fork" in network.show_active():
        pytest.skip("Only for local testing")

    supply = contract.totalSupply()    
    setMaxDrop(contract,8,3)
    
    finish_presales(contract)

    # get balance
    last_balance = contract.balance()

    contract.mint(1,{'from': get_account(1), 'value': Wei("0.055 ether")})
    
    assert contract.totalSupply() == (supply + 1)
    assert contract.ownerOf(1) == get_account(1)
    assert contract.balance() == last_balance + Wei("0.055 ether")

    # get last id generated and validate filename
    tokenId = contract.totalSupply()
    assert contract.tokenURI(tokenId) == f"https://ipfs.io/ipfs/{tokenId}.json" 

#@pytest.mark.skip(reason="focus") 
def test_can_do_mint_during_presales(contract):
    if network.show_active() not in ["development"] or "fork" in network.show_active():
        pytest.skip("Only for local testing")

    # add test accounts to the pre-sale list
    contract.addToPresalesList([get_account(1),get_account(2)],{'from': get_account(0)})

    init_presales(contract)

    # define maximum pre-sales of 3 and sales of 8 
    setMaxDrop(contract,8,3)

    # get supply and balance
    supply = contract.totalSupply()
    last_balance = contract.balance()
    
    contract.preSalesMint(1,{'from': get_account(2), 'value': Wei("0.055 ether")})

    assert contract.totalSupply() == supply + 1
    assert contract.balance() == last_balance + Wei("0.055 ether")
    assert (contract.ownerOf(1) == get_account(2))

#@pytest.mark.skip(reason="focus") 
def test_can_do_initial_mint(contract):
    if network.show_active() not in ["development"] or "fork" in network.show_active():
        pytest.skip("Only for local testing")

    supply = contract.totalSupply()

    with brownie.reverts("dev: the initial amount is exceeded"):
        contract.initialMint(200)

    contract.initialMint(50)
    contract.initialMint(50)
    contract.initialMint(50)

    assert(contract.totalSupply() == supply + 150)

    with brownie.reverts("dev: initial amount already allocated"):
        contract.initialMint(1)

#@pytest.mark.skip(reason="focus") 
def test_can_do_whitelist(contract):
    if network.show_active() not in ["development"] or "fork" in network.show_active():
        pytest.skip("Only for local testing")

    # change default 150 for maxwhitelist by 64
    contract.setMaxWhiteListAmount(64)
    whitelist(contract,64)

    
