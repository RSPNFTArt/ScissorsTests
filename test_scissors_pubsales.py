import pytest
import brownie

from decimal import *
from brownie import network, Scissors, Wei 
from scripts.helpful_scripts import get_account
from scripts.helpful_tests import create_contract,finish_presales,setMaxDrop

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

#@pytest.mark.skip(reason="focus")
def test_in_public_sales(contract):

    finish_presales(contract)

    assert(contract.inPublicSales())

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
def test_cannot_mint_below_price_pubsale(contract):
    if network.show_active() not in ["development"] or "fork" in network.show_active():
        pytest.skip("Only for local testing")

    # define maximum pre-sales of 3 and sales of 8 
    setMaxDrop(contract,8,3)

    finish_presales(contract)
    
    # Let's keep supply and balance to check no variance in supply
    supply = contract.totalSupply()
    last_balance = contract.balance()

    # max pre-sales reached (3), so next line should provide exception  
    with brownie.reverts("dev: Wrong price provided"):
        contract.mint(1,{'from': get_account(3), 'value': Wei("0.0001 ether")})

    with brownie.reverts("dev: Wrong price provided"):
        contract.mint(2,{'from': get_account(3), 'value': Wei("0.055 ether")})

    # supply should be the same
    assert contract.totalSupply() == supply
    assert contract.balance() == last_balance

#@pytest.mark.skip(reason="focus")
def test_cannot_mint_above_price_pubsale(contract):
    if network.show_active() not in ["development"] or "fork" in network.show_active():
        pytest.skip("Only for local testing")

    # define maximum pre-sales of 3 and sales of 8 
    setMaxDrop(contract,8,3)

    finish_presales(contract)

    # Let's keep supply and balance to check no variance in supply
    supply = contract.totalSupply()
    last_balance = contract.balance()

    # max pre-sales reached (3), so next line should provide exception  
    with brownie.reverts("dev: Wrong price provided"):
        contract.mint(1,{'from': get_account(5), 'value': Wei("1 ether")})

    with brownie.reverts("dev: Wrong price provided"):
        contract.mint(2,{'from': get_account(5), 'value': Wei("1 ether")})

    # supply should be the same
    assert contract.totalSupply() == supply
    assert contract.balance() == last_balance

#@pytest.mark.skip(reason="focus")
def test_cannot_mint_over_max_per_tx_limit(contract):
    if network.show_active() not in ["development"] or "fork" in network.show_active():
        pytest.skip("Only for local testing")

    # define maximum pre-sales of 3 and sales of 8 
    setMaxDrop(contract,100,4)

    finish_presales(contract)

    # set max per tx limit
    contract.setMaxSalesNFTAmount(6)

    # Let's keep supply and balance to check no variance in supply
    supply = contract.totalSupply()
    last_balance = contract.balance()

    # We should be able to perform this (not exceeding max per-tx limit)
    contract.mint(6,{'from': get_account(6), 'value': Wei("0.330 ether")})

    # here the amount should increase    
    assert contract.totalSupply() == supply + 6
    assert contract.balance() == last_balance + Wei("0.330 ether")

    # Let's keep supply and balance to check no variance in supply
    supply = contract.totalSupply()
    last_balance = contract.balance()

    # max per tx public sales limit has been reached (e.g 25), so next line should provide exception  
    with brownie.reverts("dev: Specified amount exceeds per-wallet maximum mint"):
        contract.mint(7,{'from': get_account(6), 'value': Wei("0.385 ether")})

    # supply should be the same
    assert contract.totalSupply() == supply
    assert contract.balance() == last_balance

#@pytest.mark.skip(reason="focus")
def test_sold_out_max_reached(contract):
    if network.show_active() not in ["development"] or "fork" in network.show_active():
        pytest.skip("Only for local testing")

    # define maximum pre-sales of 3 and sales of 8 
    setMaxDrop(contract,20,4)

    finish_presales(contract)

    # set max per tx limit
    contract.setMaxSalesNFTAmount(10)

    # Let's keep supply and balance to check no variance in supply
    supply = contract.totalSupply()
    last_balance = contract.balance()

    # We should be able to perform this (not exceeding max total limit yet, set in 20)
    contract.mint(6,{'from': get_account(6), 'value': Wei("0.330 ether")})
    contract.mint(10,{'from': get_account(7), 'value': Wei("0.550 ether")})
    contract.mint(4,{'from': get_account(2), 'value': Wei("0.220 ether")})
    
    # here the amount should increase    
    assert contract.totalSupply() == supply + 20
        
    # we subtract the ethers from 1st+2nd prize (4+5 ethers)
    assert contract.balance() == last_balance + Wei("1.1 ether") - Wei("9 ether")
    
    # Let's keep supply and balance to check no variance in supply
    supply = contract.totalSupply()
    last_balance = contract.balance()

    assert(contract.publicSalesFinished())

    # max per tx public sales limit has been reached (e.g 25), so next line should provide exception  
    with brownie.reverts("dev: SOLD OUT!"):
        contract.mint(1,{'from': get_account(8), 'value': Wei("0.055 ether")})

    # supply should be the same
    assert contract.totalSupply() == supply
    assert contract.balance() == last_balance 

    assert(contract.publicSalesFinished())

    # max per tx public sales limit has been reached (e.g 25), so next line should provide exception  
    with brownie.reverts("dev: SOLD OUT!"):
        contract.mint(4,{'from': get_account(6), 'value': Wei("0.220 ether")})

    # supply should be the same
    assert contract.totalSupply() == supply    
    assert contract.balance() == last_balance 

    # each account should have the expected number of ERC-720 tokens
    assert contract.balanceOf(get_account(6)) == 6
    assert contract.balanceOf(get_account(7)) == 10
    assert contract.balanceOf(get_account(2)) == 4
    
    # check TH is reserved 
    assert contract.reservedTHPrize() == Wei("50 ether")
    
#@pytest.mark.skip(reason="focus")
def test_cannot_mint_during_pause(contract):
    if network.show_active() not in ["development"] or "fork" in network.show_active():
        pytest.skip("Only for local testing")

    # define maximum pre-sales of 3 and sales of 8 
    setMaxDrop(contract,8,3)

    assert(not contract.inPublicSales())

    # disable preSales mode
    contract.preSalesOff()

    # we need to complete presales before we can start minting in public sales
    # contract is paused here
    contract.preSalesComplete()
    assert(contract.preSalesFinished())
    assert(not contract.inPresales())
    assert(not contract.inPublicSales())

    # Let's keep supply and balance to check no variance in supply
    supply = contract.totalSupply()
    last_balance = contract.balance()

    # max pre-sales reached (3), so next line should provide exception  
    with brownie.reverts("dev: Minting is paused"):
        contract.mint(1,{'from': get_account(3), 'value': Wei("0.0001 ether")})

    # supply should be the same
    assert contract.totalSupply() == supply
    assert contract.balance() == last_balance 

#@pytest.mark.skip(reason="focus")
def test_cannot_zero_mint(contract):
    if network.show_active() not in ["development"] or "fork" in network.show_active():
        pytest.skip("Only for local testing")

    # define maximum pre-sales of 3 and sales of 8 
    setMaxDrop(contract,15,4)

    finish_presales(contract)

    # set max per tx limit
    contract.setMaxSalesNFTAmount(6)

    # Let's keep supply and balance to check no variance in supply
    supply = contract.totalSupply()
    last_balance = contract.balance()

    # should not raise exception but should not mint (though gas is spent)
    contract.mint(0,{'from': get_account(6), 'value': Wei("0.0 ether")})

    # here the amount should increase    
    assert contract.totalSupply() == supply
    assert contract.balance() == last_balance

#@pytest.mark.skip(reason="focus")
def test_burn_tokens(contract):
    if network.show_active() not in ["development"] or "fork" in network.show_active():
        pytest.skip("Only for local testing")

    th_balance = contract.reservedTHPrize()

    setMaxDrop(contract,400,3)
    
    finish_presales(contract)

    # mint 10% (40)
    contract.mint(10,{'from': get_account(14), 'value': Wei("0.55 ether")})
    contract.mint(10,{'from': get_account(15), 'value': Wei("0.55 ether")})
    contract.mint(10,{'from': get_account(16), 'value': Wei("0.55 ether")})
    contract.mint(10,{'from': get_account(17), 'value': Wei("0.55 ether")})

    # burn item #10
    contract.burn(10,{'from': get_account(14)})
    
    assert(contract.getMaxDrop() == 399)

    with brownie.reverts("dev: cannot set maxDrop below already supply"):
        contract.setMaxDrop(10)

    contract.setMaxDrop(100)

    assert(contract.getMaxDrop() == 100)

    # This means 25% has been dropped  (40 > 25)
    # Let's confirm TH is expected one  
    assert contract.reservedTHPrize() == th_balance + Wei("5 ether")
