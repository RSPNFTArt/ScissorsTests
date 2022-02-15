import pytest
import brownie

from decimal import *
from brownie import network, Scissors, Wei, exceptions
from scripts.helpful_scripts import get_account
from scripts.helpful_tests import create_contract,init_presales,finish_presales,setMaxDrop

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
def test_cannot_mint_scissor_public_sales_during_presales(contract):
    if network.show_active() not in ["development"] or "fork" in network.show_active():
        pytest.skip("Only for local testing")

    supply = contract.totalSupply()    
    setMaxDrop(contract,8,3)
    
    # "Pre-sales has not started yet or wallet not eligible"
    with brownie.reverts("dev: Pre-sales has not finished yet"):
        contract.mint(1,{'from': get_account(1), 'value': Wei("0.055 ether")})

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

# If pre-sales period is not activated yet we cannot mint even if added to the list
#@pytest.mark.skip(reason="focus")
def test_cannot_purchase_outside_presales(contract):
    if network.show_active() not in ["development"] or "fork" in network.show_active():
        pytest.skip("Only for local testing")

    setMaxDrop(contract,15,5)
    contract.preSalesOff()
    
    contract.addToPresalesList([get_account(1)],{'from': get_account(0)})

    # get supply and balance 
    supply = contract.totalSupply()    
    last_balance = contract.balance()

    # "Pre-sales has not started yet or wallet not eligible"
    with brownie.reverts("dev: Pre-sales has not started yet"):
        contract.preSalesMint(1,{'from': get_account(1), 'value': Wei("0.055 ether")})

    assert contract.totalSupply() == supply
    assert contract.balance() == last_balance 

#@pytest.mark.skip(reason="focus")
def test_am_i_in_presales(contract):
    init_presales(contract)

    # add test accounts to the pre-sale list
    contract.addToPresalesList([get_account(9),get_account(3)],{'from': get_account(0)})
    
    assert contract.AmIinPresales({'from': get_account(3)})
    assert contract.AmIinPresales({'from': get_account(9)})
    assert not (contract.AmIinPresales({'from': get_account(5)}))

#@pytest.mark.skip(reason="focus")
def test_addr_in_presales(contract):
    init_presales(contract)

    # add test accounts to the pre-sale list
    contract.addToPresalesList([get_account(9),get_account(3)],{'from': get_account(0)})
    
    assert contract.AddrInPresales(get_account(3))
    assert contract.AddrInPresales(get_account(9))
    assert not (contract.AddrInPresales(get_account(5)))

#@pytest.mark.skip(reason="focus")
def test_in_presales(contract):
    
    init_presales(contract)

    contract.preSalesComplete({'from': get_account(0)})
    assert(contract.preSalesFinished())
    assert(not contract.inPresales())

#@pytest.mark.skip(reason="focus")
# If pre-sales period has finished we cannot mint even if added to the list
def test_cannot_do_presales_mint_when_finished(contract):
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

    assert(not contract.inPublicSales())

    contract.preSalesMint(2,{'from': get_account(1), 'value': Wei("0.110 ether")})
    
    assert contract.totalSupply() == supply + 2
    assert contract.balance() == last_balance + Wei("0.110 ether")
    assert (contract.ownerOf(1) == get_account(1) and 
           contract.ownerOf(2) == get_account(1))
    assert(contract.tokenURI(1) == f"https://ipfs.io/ipfs/1.json" and 
            contract.tokenURI(2) == f"https://ipfs.io/ipfs/2.json")

    finish_presales(contract)

    # pre-sales has finished and even there's minting left (1 left as we did 2 of the 3)
    # and account 2 in the list, we throw exception  
    with brownie.reverts("dev: Pre-sales has already finished"):
        contract.preSalesMint(1,{'from': get_account(2), 'value': Wei("0.055 ether")})
    
# Only a set of wallets will be able to mint during presales
#@pytest.mark.skip(reason="focus")
def test_cannot_mint_presales_if_not_elligible(contract):
    if network.show_active() not in ["development"] or "fork" in network.show_active():
        pytest.skip("Only for local testing")

    setMaxDrop(contract,15,5)
    
    init_presales(contract)

    # get supply and balance 
    supply = contract.totalSupply()    
    last_balance = contract.balance()
    
    # Wallet not eligible
    with pytest.raises(exceptions.VirtualMachineError) as excinfo:
        contract.preSalesMint(1,{'from': get_account(1), 'value': Wei("0.055 ether")})

    assert contract.totalSupply() == supply
    assert contract.balance() == last_balance 
    assert "is missing role" in str(excinfo.value)

#@pytest.mark.skip(reason="focus")
def test_cannot_exceed_per_wallet_amount_presales(contract):
    if network.show_active() not in ["development"] or "fork" in network.show_active():
        pytest.skip("Only for local testing")

    # add test accounts to the pre-sale list
    contract.addToPresalesList([get_account(2)],{'from': get_account(0)})

    init_presales(contract)
    
    # define maximum pre-sales of 3 and sales of 8 
    setMaxDrop(contract,8,3)

    contract.preSalesMint(2,{'from': get_account(2), 'value': Wei("0.110 ether")})
    
    # get supply and balance
    supply = contract.totalSupply()
    last_balance = contract.balance()

    # max pre-sales reached per wallet (e.g 2), so next line should provide exception  
    with brownie.reverts("dev: Total pre-sales amount exceeded for wallet"):
        contract.preSalesMint(1,{'from': get_account(2), 'value': Wei("0.055 ether")})

    assert contract.totalSupply() == supply
    assert contract.balance() == last_balance
    assert (contract.ownerOf(1) == get_account(2) and 
           contract.ownerOf(2) == get_account(2))
    assert (contract.tokenURI(1) == f"https://ipfs.io/ipfs/1.json" and
           contract.tokenURI(2) == f"https://ipfs.io/ipfs/2.json") 
    
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
    
    contract.preSalesMint(2,{'from': get_account(1), 'value': Wei("0.110 ether")})
    contract.preSalesMint(1,{'from': get_account(2), 'value': Wei("0.055 ether")})

    assert contract.totalSupply() == supply + 3
    assert contract.balance() == last_balance + Wei("0.165 ether")
    assert (contract.ownerOf(1) == get_account(1) and 
           contract.ownerOf(2) == get_account(1) and
           contract.ownerOf(3) == get_account(2))
    assert(contract.tokenURI(1) == f"https://ipfs.io/ipfs/1.json" and 
            contract.tokenURI(2) == f"https://ipfs.io/ipfs/2.json" and 
            contract.tokenURI(3) == f"https://ipfs.io/ipfs/3.json")

# Requirement is that we cannot mint further than the max number allocated for the pre-sales 
# e.g 275x2 NFTs 
#@pytest.mark.skip(reason="focus")
def test_cannot_mint_over_max_presale(contract):
    if network.show_active() not in ["development"] or "fork" in network.show_active():
        pytest.skip("Only for local testing")

    # add test accounts to the pre-sale list
    contract.addToPresalesList([get_account(1),get_account(2)],{'from': get_account(0)})

    init_presales(contract)

    # define maximum pre-sales of 3 and sales of 8 
    setMaxDrop(contract,8,3)

    contract.preSalesMint(2,{'from': get_account(1), 'value': Wei("0.110 ether")})
    contract.preSalesMint(1,{'from': get_account(2), 'value': Wei("0.055 ether")})

    # get supply and balance
    supply = contract.totalSupply()
    last_balance = contract.balance()

    assert(contract.preSalesFinished())

    # max pre-sales reached (3), so next line should provide exception  
    with brownie.reverts("dev: Pre-sales SOLD-OUT"):
        contract.preSalesMint(1,{'from': get_account(2), 'value': Wei("0.055 ether")})

    assert contract.totalSupply() == supply
    assert contract.balance() == last_balance
    assert (contract.ownerOf(1) == get_account(1) and 
           contract.ownerOf(2) == get_account(1) and
           contract.ownerOf(3) == get_account(2))
    assert(contract.tokenURI(1) == f"https://ipfs.io/ipfs/1.json" and 
            contract.tokenURI(2) == f"https://ipfs.io/ipfs/2.json" and 
            contract.tokenURI(3) == f"https://ipfs.io/ipfs/3.json")

# To ensure we get error if using preSalesMint function after presales mode is  off
#@pytest.mark.skip(reason="focus")
def test_cannot_perform_mint_after_presales(contract):
    if network.show_active() not in ["development"] or "fork" in network.show_active():
        pytest.skip("Only for local testing")

    # We need to add the given account to the pre-sales list to pretend that account will get
    # the proper message after pre-sales
    contract.addToPresalesList([get_account(3)],{'from': get_account(0)})

    # define maximum pre-sales of 3 and sales of 8 
    setMaxDrop(contract,8,3)

    finish_presales(contract)

    # get supply and balance 
    supply = contract.totalSupply()
    last_balance = contract.balance()

    # pre-sales has finished, so we cannot perform presales minting  
    with brownie.reverts("dev: Pre-sales has already finished"):
        contract.preSalesMint(1,{'from': get_account(3), 'value': Wei("0.055 ether")})

    # supply should be the same
    assert contract.totalSupply() == supply
    assert contract.balance() == last_balance

#@pytest.mark.skip(reason="focus")
def test_cannot_mint_in_presales_below_price(contract):
    if network.show_active() not in ["development"] or "fork" in network.show_active():
        pytest.skip("Only for local testing")

    # add test accounts to the pre-sale list
    contract.addToPresalesList([get_account(3)],{'from': get_account(0)})

    # define maximum pre-sales of 3 and sales of 8 
    setMaxDrop(contract,8,3)

    init_presales(contract)

    # Let's keep supply and balance to check no variance in supply
    supply = contract.totalSupply()
    last_balance = contract.balance()

    # max pre-sales reached (3), so next line should provide exception  
    with brownie.reverts("dev: Wrong price provided"):
        contract.preSalesMint(1,{'from': get_account(3), 'value': Wei("0.0001 ether")})

    with brownie.reverts("dev: Wrong price provided"):
        contract.preSalesMint(2,{'from': get_account(3), 'value': Wei("0.055 ether")})

    # supply should be the same
    assert contract.totalSupply() == supply
    assert contract.balance() == last_balance

#@pytest.mark.skip(reason="focus")
def test_cannot_mint_in_presales_above_price(contract):
    if network.show_active() not in ["development"] or "fork" in network.show_active():
        pytest.skip("Only for local testing")

    # add test accounts to the pre-sale list
    contract.addToPresalesList([get_account(5)],{'from': get_account(0)})

    # define maximum pre-sales of 3 and sales of 8 
    setMaxDrop(contract,8,3)

    init_presales(contract)

    # Let's keep to check no variance in supply
    supply = contract.totalSupply()
    last_balance = contract.balance()

    # max pre-sales reached (3), so next line should provide exception  
    with brownie.reverts("dev: Wrong price provided"):
        contract.preSalesMint(1,{'from': get_account(5), 'value': Wei("1 ether")})

    with brownie.reverts("dev: Wrong price provided"):
        contract.preSalesMint(2,{'from': get_account(5), 'value': Wei("1 ether")})

    # supply should be the same
    assert contract.totalSupply() == supply
    assert contract.balance() == last_balance
        
#@pytest.mark.skip(reason="focus")
def test_cannot_mint_in_presales_during_pause(contract):
    if network.show_active() not in ["development"] or "fork" in network.show_active():
        pytest.skip("Only for local testing")

    # Pause Contract
    contract.pause()

    # add test accounts to the pre-sale list
    contract.addToPresalesList([get_account(5)],{'from': get_account(0)})

    # define maximum pre-sales of 3 and sales of 8 
    setMaxDrop(contract,8,3)

    init_presales(contract)

    # Let's keep supply and balance to check no variance in supply
    supply = contract.totalSupply()
    last_balance = contract.balance()

    # should raise exception  
    with brownie.reverts("dev: Minting is paused"):
        contract.preSalesMint(1,{'from': get_account(5), 'value': Wei("0.055 ether")})

    # supply should be the same
    assert contract.totalSupply() == supply
    assert contract.balance() == last_balance

#@pytest.mark.skip(reason="focus")
def test_cannot_zero_presales_mint(contract):
    if network.show_active() not in ["development"] or "fork" in network.show_active():
        pytest.skip("Only for local testing")

    # add test accounts to the pre-sale list
    contract.addToPresalesList([get_account(5)],{'from': get_account(0)})

    # define maximum pre-sales of 3 and sales of 8 
    setMaxDrop(contract,8,3)

    init_presales(contract)

    # Let's keep supply and balance to check no variance in supply
    supply = contract.totalSupply()
    last_balance = contract.balance()

    # should not raise exception but no change in minting (though caller spends gas)
    contract.preSalesMint(0,{'from': get_account(5), 'value': Wei("0 ether")})

    # supply should be the same
    assert contract.totalSupply() == supply
    assert contract.balance() == last_balance 
