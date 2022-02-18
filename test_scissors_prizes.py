# 
# (c) 2022, rpsnft.art
#

import pytest
import brownie
import numpy as np

from decimal import *
from brownie import network, Scissors, Wei 
from scripts.helpful_scripts import get_account, amount_in_wei
from scripts.helpful_tests import create_contract,finish_presales,first_prize_sent,\
                    get_founder_balance,second_prize_sent,third_prize_sent,withdrawn_checks,pct_at_25,\
                    pct_at_50, pct_at_75, mint_everything, get_founder_accts, register_teams,\
                    whitelist, init_presales, setMaxDrop,second_give_away_case,\
                    PRESALES_FLOAT_VAL,PUBSALES_FLOAT_VAL

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
def test_th_filled_at_25_pct(contract):
    if network.show_active() not in ["development"] or "fork" in network.show_active():
        pytest.skip("Only for local testing")

    # define maximum pre-sales of 3 and sales of 8 
    setMaxDrop(contract,80,4)

    # set max per tx limit
    contract.setMaxSalesNFTAmount(20)

    # mint 5 (up to 25%)
    pct_at_25(contract,80)

#@pytest.mark.skip(reason="focus")
def test_th_filled_at_50_pct(contract):

    if network.show_active() not in ["development"] or "fork" in network.show_active():
        pytest.skip("Only for local testing")

    # define maximum pre-sales of 3 and sales of 8 
    setMaxDrop(contract,80,4)

    # set max per tx limit
    contract.setMaxSalesNFTAmount(20)

    # mint 5 (up to 25%)
    pct_at_25(contract,80)

    # mint 5 (up to 50%)
    pct_at_50(contract,80)

#@pytest.mark.skip(reason="focus")
def test_th_filled_at_75_pct(contract):
    if network.show_active() not in ["development"] or "fork" in network.show_active():
        pytest.skip("Only for local testing")

    # define maximum pre-sales of 3 and sales of 8 
    setMaxDrop(contract,80,4)

    # set max per tx limit
    contract.setMaxSalesNFTAmount(20)

    # mint 5 (up to 25%)
    pct_at_25(contract,80)

    # mint 5 (up to 50%)
    pct_at_50(contract,80)

    # mint 5 (up to 75%)
    pct_at_75(contract,80)

#@pytest.mark.skip(reason="focus")
def test_th_filled_at_100_pct(contract):
    if network.show_active() not in ["development"] or "fork" in network.show_active():
        pytest.skip("Only for local testing")

    # define maximum pre-sales of 3 and sales of 8 
    setMaxDrop(contract,80,4)

    # set max per tx limit
    contract.setMaxSalesNFTAmount(20)

    # mint to 100%
    mint_everything(contract,80)

#@pytest.mark.skip(reason="focus")
def test_withdrawn_eths_in_founder_accounts(contract):
    if network.show_active() not in ["development"] or "fork" in network.show_active():
        pytest.skip("Only for local testing")

    # Set founder accounts
    (ss,rb,pj,rl,sp,ngo,mk,do) = get_founder_accts(contract)

    # Get founders' balances
    (ss_balance,rb_balance,pj_balance,rl_balance,sp_balance,ngo_balance,mk_balance,do_balance) = \
        get_founder_balance(ss,rb,pj,rl,sp,ngo,mk,do)
     
    # define maximum pre-sales of 3 and sales of 8 
    setMaxDrop(contract,40,4)

    # set max per tx limit
    contract.setMaxSalesNFTAmount(10)

    # mint to 100%
    mint_everything(contract,40)    

    # to avoid collisions of 2nd prize VIP accounts with expected amounts
    second_prize_sent(contract)

    # Get maximum to withdraw based on TH parts released
    max_balance = contract.maxBalanceToWithdraw()

    # Cannot withdraw without vip_tokens set
    with brownie.reverts("dev: VIP tokens unknown"):
        contract.withdraw({'from': get_account(0)})

    # set wrong number of tokens for VIPs (> 20)
    vip_tokens = [1,3,4,5,6,7,8,9,10,11,13,15,16,17,18,19,20,21,22,23,24]
    with brownie.reverts("dev: max number of VIPs is 20"):
        contract.setVIPTokens(vip_tokens)

    vip_tokens = []
    with brownie.reverts("dev: no tokens of VIPs provided"):
        contract.setVIPTokens(vip_tokens)

    # set tokens for VIPs
    vip_tokens = [1,3,5,6,8,11,13,15,17,18]  
    contract.setVIPTokens(vip_tokens)

    # Request withdrawing
    contract.withdraw({'from': get_account(0)})

    # Calc expected stakes
    # np.asarray transforms tuple returned by get_founder_balance into expected array
    current_balance = np.asarray(get_founder_balance(ss,rb,pj,rl,sp,ngo,mk,do))
    previous_balance = [ss_balance,rb_balance,pj_balance,
                        rl_balance, sp_balance, ngo_balance,
                        mk_balance,do_balance]
    
    #
    # As every vip owner account may have more than one card, let's 
    # list the accounts (accs_vip)
    # list the amount per account (mult_vip_expected)
    # then withdrawn_checks will use these multipliers to confirm the amounts 
    # actually allocated correspond to the expected amounts
    #
    accs_vip = [6,5,3,8]  
    mult_vip_expected = [1,1,3,5]

    withdrawn_checks(contract,max_balance,vip_tokens,current_balance,previous_balance,
                         accs_vip,
                         mult_vip_expected) 

#@pytest.mark.skip(reason="focus")
def test_withdrawn_eths_in_founder_accounts_in_two_parts(contract):
    if network.show_active() not in ["development"] or "fork" in network.show_active():
        pytest.skip("Only for local testing")

    # Set founder accounts
    (ss,rb,pj,rl,sp,ngo,mk,do) = get_founder_accts(contract)

    # Get founders' balances
    (ss_balance,rb_balance,pj_balance,rl_balance,sp_balance,ngo_balance,mk_balance,do_balance) = \
        get_founder_balance(ss,rb,pj,rl,sp,ngo,mk,do)

    # Get contract balance
    init_balance = contract.balance()
    last_balance = init_balance
    
    # define maximum pre-sales of 3 and sales of 8 
    setMaxDrop(contract,40,4)

    # set max per tx limit
    contract.setMaxSalesNFTAmount(10)

    # mint 10 (up to 25%)
    pct_at_25(contract,40)
    
    # Let's even mint more
    contract.mint(7,{'from': get_account(21), 'value': amount_in_wei(PUBSALES_FLOAT_VAL*7)})

    # Minted 17, 25% of 40 = 10 so, not reaching to 50%
    # max_balance = last_balance - 5 ether (25% reserved) - 10 ether next part when we reach 50%
    max_balance = contract.maxBalanceToWithdraw()
    last_balance = contract.balance()
    assert max_balance == last_balance - Wei("5 ether") - Wei("10 ether") - Wei("4 ether")
    assert contract.reservedTHPrize() == Wei("5 ether")

    # Cannot withdraw without vip_tokens set
    with brownie.reverts("dev: VIP tokens unknown"):
        contract.withdraw({'from': get_account(0)})

    # set wrong number of tokens for VIPs (> 20)
    vip_tokens = [1,3,4,5,6,7,8,9,10,11,13,15,16,17,18,19,20,21,22,23,24]
    with brownie.reverts("dev: max number of VIPs is 20"):
        contract.setVIPTokens(vip_tokens)

    vip_tokens = []
    with brownie.reverts("dev: no tokens of VIPs provided"):
        contract.setVIPTokens(vip_tokens)

    # set tokens for VIPs (<10 validated)
    vip_tokens = [1,3,5,8,10]
    contract.setVIPTokens(vip_tokens)

    # Request withdrawing
    contract.withdraw({'from': get_account(0)})
    last_balance = contract.balance()
    # everything so far withdrawn
    assert contract.maxBalanceToWithdraw() == 0

    # We have not reached 50%, so after withdrawn contract balance should 
    # be 5 ether (in pool), 10 ether (waiting for next TH) + 4 ether (1st prize)
    assert last_balance == Wei("5 ether") + Wei("10 ether") + Wei("4 ether")

    # Calc expected stakes
    current_balance = np.asarray(get_founder_balance(ss,rb,pj,rl,sp,ngo,mk,do))
    previous_balance = [ss_balance,rb_balance,pj_balance,
                        rl_balance, sp_balance, ngo_balance,
                        mk_balance,do_balance]
    accs_vip = [6,5,3]
    mult_vip_expected = [1,1,3]
    withdrawn_checks(contract,max_balance,vip_tokens,current_balance,previous_balance,
                         accs_vip,
                         mult_vip_expected) 

    # Validate 2nd time after previous withdraw

    # Get founders' balances
    (ss_balance,rb_balance,pj_balance,rl_balance,sp_balance,ngo_balance,mk_balance,do_balance) = \
        get_founder_balance(ss,rb,pj,rl,sp,ngo,mk,do)
  
    # Get contract balance
    last_balance = contract.balance()

    # Let's now mint after withdrawn     
    contract.mint(7,{'from': get_account(21), 'value': amount_in_wei(PUBSALES_FLOAT_VAL*7)})

    # Minted 17+7 (24), 50% of 40 = 20 so
    #  1.- last_balance = (-10 that are moved to TH) + (-4 for 1st prize) + amount_in_wei(PUBSALES_FLOAT_VAL*7)
    #      from recent purchase. No more than amount_in_wei(PUBSALES_FLOAT_VAL*7) as we have withdrawn
    #  2.- max_balance = last_balance - 15 ether, so max_balance = 0   

    max_balance = contract.maxBalanceToWithdraw()
    last_balance = contract.balance()
    assert last_balance == Wei("5 ether") + Wei("10 ether") + amount_in_wei(PUBSALES_FLOAT_VAL*7)
    assert max_balance == 0 

    # we now charge contract with +35 ether 
    # new max_balance = 35.231 - 15 ether (3rd part TH) - 5 ether (2nd prize)= 15.231
    contract.chargeContract({'from': get_account(22), 
                            'value': Wei("35 ether")})
    max_balance = contract.maxBalanceToWithdraw()
    last_balance = contract.balance()

    # the max balance is the existing balance subtracting the reserve for TH
    # as we have past 50% we are preserving following amounts from withdrawn:
    #   TH 5+10 (from first two quarters) + future quarter (15 TH)
    #   5 ETH from 2nd prize for future quarter (2nd prize)
    #   4 ETH were already provided so are discounted in last_balance
    assert max_balance == last_balance - Wei("15 ether") - Wei("10 ether") - Wei("5 ether") - Wei("5 ether") 

    contract.withdraw({'from': get_account(0)})

    # Calc expected stakes
    current_balance = np.asarray(get_founder_balance(ss,rb,pj,rl,sp,ngo,mk,do))
    previous_balance = [ss_balance,rb_balance,pj_balance,
                        rl_balance, sp_balance, ngo_balance,
                        mk_balance,do_balance]
    
    # reusing accs_vip and mult_vip_expected
    withdrawn_checks(contract,max_balance,vip_tokens,current_balance,previous_balance,
                         accs_vip,
                         mult_vip_expected) 
  
    # everything so far withdrawn
    assert contract.maxBalanceToWithdraw() == 0
    
    # Contract balance now reserves 
    # 5 ether (TH, 1st part)
    # 10 ether (TH, 2nd part)
    # 15 ether (TH, 3rd part) 
    # and 5 ether for 2nd prize
    assert contract.balance() == Wei("5 ether") + Wei("10 ether") + Wei("15 ether") + Wei("5 ether") 
    assert contract.reservedTHPrize() == Wei("15 ether")

#@pytest.mark.skip(reason="focus")
def test_eth_first_give_away_can_pull_transfers(contract):
    if network.show_active() not in ["development"] or "fork" in network.show_active():
        pytest.skip("Only for local testing")

    # set the number of maximum drops to achieve 50% quicker during test
    setMaxDrop(contract,8,3)

    assert(not contract.inPublicSales())

    finish_presales(contract)

    # Prepare winners list 
    winners = [get_account(11), get_account(12), get_account(13)]

    assert not contract.pctReached(50)

    # We cannot send give away yet
    with brownie.reverts("dev: 50% not achieved yet"):
        contract.sendGiveAway(1, winners)

    # we mint 50% (4 of 8)
    contract.mint(4,{'from': get_account(18), 'value': amount_in_wei(PUBSALES_FLOAT_VAL*4)})

    first_prize_sent(contract)

#@pytest.mark.skip(reason="focus")
def test_eth_first_give_away_cannot_be_pulled_by_non_winners(contract):
    if network.show_active() not in ["development"] or "fork" in network.show_active():
        pytest.skip("Only for local testing")

    setMaxDrop(contract,8,3)

    assert(not contract.inPublicSales())

    finish_presales(contract)

    # Prepare winners list 
    winners = [get_account(11), get_account(12), get_account(13)]
    
    # We cannot send give away yet
    with brownie.reverts("dev: 50% not achieved yet"):
        contract.sendGiveAway(1, winners)

    # we mint 50%
    contract.mint(4,{'from': get_account(18), 'value': amount_in_wei(PUBSALES_FLOAT_VAL*4)})

    first_prize_sent(contract,False)

#@pytest.mark.skip(reason="focus")
def test_eth_second_give_away_can_pull_transfers(contract):
    if network.show_active() not in ["development"] or "fork" in network.show_active():
        pytest.skip("Only for local testing")
    
    second_give_away_case(contract)


#@pytest.mark.skip(reason="focus")
def test_eth_second_give_away_cannot_be_pulled_by_non_winners(contract):
    if network.show_active() not in ["development"] or "fork" in network.show_active():
        pytest.skip("Only for local testing")

    second_give_away_case(contract,False)


#@pytest.mark.skip(reason="focus")
def test_eth_third_give_away_can_pull_transfers(contract):
    if network.show_active() not in ["development"] or "fork" in network.show_active():
        pytest.skip("Only for local testing")

    contract.setSecret(0xc400cda91a2ade601f638972b9ff78851ab8e8bef801f0fe79680d215190cca0)
        
    setMaxDrop(contract,200,12)

    # set max per tx limit
    contract.setMaxSalesNFTAmount(25)

    init_presales(contract)
    
    # add test accounts to the pre-sale list
    contract.addToPresalesList([get_account(3),get_account(4),get_account(7)],{'from': get_account(0)})
    
    # break it in two to allow adding later 
    contract.addToPresalesList([get_account(8),get_account(9),get_account(10)],{'from': get_account(0)})
    
    # Account 2 is the TH account (see module-scope test in the top). Get baseline for TH account
    th_balance = contract.reservedTHPrize()

    # presales is just 10 (not yet 25%)
    contract.preSalesMint(2,{'from': get_account(3), 'value': amount_in_wei(PRESALES_FLOAT_VAL*2)})
    contract.preSalesMint(2,{'from': get_account(4), 'value': amount_in_wei(PRESALES_FLOAT_VAL*2)})
    contract.preSalesMint(2,{'from': get_account(8), 'value': amount_in_wei(PRESALES_FLOAT_VAL*2)})
    contract.preSalesMint(2,{'from': get_account(9), 'value': amount_in_wei(PRESALES_FLOAT_VAL*2)})
    contract.preSalesMint(2,{'from': get_account(10), 'value': amount_in_wei(PRESALES_FLOAT_VAL*2)})

    # TH balance should be the same as we have not pass the 25% of max (5 = 20/4)
    assert contract.reservedTHPrize() == th_balance
    
    finish_presales(contract)

    # allow whitelist (-150)
    # During real execution we would run whitelist before presales but tests accounts 
    # but we can run it anytime and current tests are based on accounts from pre-sales
    # so to avoid affecting the expected results we move this after presales are finished
    whitelist(contract,150)

    # Let's keep to check no variance in supply
    supply = contract.totalSupply()

    # supply = 150 (whitelist) + 10 (presales)
    assert supply == 160 

    # we mint 100% (40) among 12 different accounts 
    contract.mint(3,{'from': get_account(6), 'value': amount_in_wei(PUBSALES_FLOAT_VAL*3)})
    contract.mint(3,{'from': get_account(9), 'value': amount_in_wei(PUBSALES_FLOAT_VAL*3)})
    contract.mint(3,{'from': get_account(10), 'value': amount_in_wei(PUBSALES_FLOAT_VAL*3)})
    contract.mint(3,{'from': get_account(11), 'value': amount_in_wei(PUBSALES_FLOAT_VAL*3)})
    contract.mint(3,{'from': get_account(12), 'value': amount_in_wei(PUBSALES_FLOAT_VAL*3)})
    contract.mint(3,{'from': get_account(13), 'value': amount_in_wei(PUBSALES_FLOAT_VAL*3)})
    contract.mint(3,{'from': get_account(16), 'value': amount_in_wei(PUBSALES_FLOAT_VAL*3)})
    contract.mint(3,{'from': get_account(17), 'value': amount_in_wei(PUBSALES_FLOAT_VAL*3)})
    contract.mint(3,{'from': get_account(18), 'value': amount_in_wei(PUBSALES_FLOAT_VAL*3)})
    contract.mint(3,{'from': get_account(19), 'value': amount_in_wei(PUBSALES_FLOAT_VAL*3)})
    contract.mint(2,{'from': get_account(14), 'value': amount_in_wei(PUBSALES_FLOAT_VAL*2)})
    contract.mint(2,{'from': get_account(15), 'value': amount_in_wei(PUBSALES_FLOAT_VAL*2)})
    contract.mint(2,{'from': get_account(8), 'value': amount_in_wei(PUBSALES_FLOAT_VAL*2)})
    contract.mint(2,{'from': get_account(5), 'value': amount_in_wei(PUBSALES_FLOAT_VAL*2)})
    contract.mint(2,{'from': get_account(7), 'value': amount_in_wei(PUBSALES_FLOAT_VAL*2)})
    
    assert(contract.ownerOf(161) == get_account(6))
    assert(contract.ownerOf(162) == get_account(6))
    assert(contract.ownerOf(163) == get_account(6))
    
    assert(contract.ownerOf(173) == get_account(12))
    assert(contract.ownerOf(174) == get_account(12))
    assert(contract.ownerOf(175) == get_account(12))
    
    assert(contract.ownerOf(176) == get_account(13))
    assert(contract.ownerOf(177) == get_account(13))
    assert(contract.ownerOf(178) == get_account(13))

    # register team of 8 
    register_teams(contract,"wonderful", 
        [get_account(6),[161,162,163],
        get_account(12),[173,175],
        get_account(13),[176,177,178],
        get_account(17),[182,183]])

    register_teams(contract,"locos",
    [get_account(16),[179],
     get_account(18),[185],
     get_account(19),[189],
     get_account(14),[192]])

    third_prize_sent(contract,get_account(1), get_account(6), get_account(12))

#@pytest.mark.skip(reason="focus")
def test_eth_third_give_away_cannot_be_pulled_by_non_winners(contract):
    if network.show_active() not in ["development"] or "fork" in network.show_active():
        pytest.skip("Only for local testing")

    contract.setSecret(0xc400cda91a2ade601f638972b9ff78851ab8e8bef801f0fe79680d215190cca0)
        
    setMaxDrop(contract,200,12)

    # set max per tx limit
    contract.setMaxSalesNFTAmount(25)

    init_presales(contract)
    
    # add test accounts to the pre-sale list
    contract.addToPresalesList([get_account(3),get_account(4),get_account(7)],{'from': get_account(0)})
    
    # break it in two to allow adding later 
    contract.addToPresalesList([get_account(8),get_account(9),get_account(10)],{'from': get_account(0)})
    
    # Account 2 is the TH account (see module-scope test in the top). Get baseline for TH account
    th_balance = get_account(2).balance()

    # presales is just 10 (not yet 25%)
    contract.preSalesMint(2,{'from': get_account(3), 'value': amount_in_wei(PRESALES_FLOAT_VAL*2)})
    contract.preSalesMint(2,{'from': get_account(4), 'value': amount_in_wei(PRESALES_FLOAT_VAL*2)})
    contract.preSalesMint(2,{'from': get_account(8), 'value': amount_in_wei(PRESALES_FLOAT_VAL*2)})
    contract.preSalesMint(2,{'from': get_account(9), 'value': amount_in_wei(PRESALES_FLOAT_VAL*2)})
    contract.preSalesMint(2,{'from': get_account(10), 'value': amount_in_wei(PRESALES_FLOAT_VAL*2)})

    # TH balance should be the same as we have not pass the 25% of max (5 = 20/4)
    assert get_account(2).balance() == th_balance
    
    finish_presales(contract)

    # allow whitelist (-150)
    # During real execution we would run whitelist before presales but tests accounts 
    # but we can run it anytime and current tests are based on accounts from pre-sales
    # so to avoid affecting the expected results we move this after presales are finished
    whitelist(contract,150)

    # Let's keep to check no variance in supply
    supply = contract.totalSupply()

    # supply = 150 (whitelist) + 10 (presales)
    assert supply == 160 

    # we mint 100% (40) among 12 different accounts 
    contract.mint(3,{'from': get_account(6), 'value': amount_in_wei(PUBSALES_FLOAT_VAL*3)})
    contract.mint(3,{'from': get_account(9), 'value': amount_in_wei(PUBSALES_FLOAT_VAL*3)})
    contract.mint(3,{'from': get_account(10), 'value': amount_in_wei(PUBSALES_FLOAT_VAL*3)})
    contract.mint(3,{'from': get_account(11), 'value': amount_in_wei(PUBSALES_FLOAT_VAL*3)})
    contract.mint(3,{'from': get_account(12), 'value': amount_in_wei(PUBSALES_FLOAT_VAL*3)})
    contract.mint(3,{'from': get_account(13), 'value': amount_in_wei(PUBSALES_FLOAT_VAL*3)})
    contract.mint(3,{'from': get_account(16), 'value': amount_in_wei(PUBSALES_FLOAT_VAL*3)})
    contract.mint(3,{'from': get_account(17), 'value': amount_in_wei(PUBSALES_FLOAT_VAL*3)})
    contract.mint(3,{'from': get_account(18), 'value': amount_in_wei(PUBSALES_FLOAT_VAL*3)})
    contract.mint(3,{'from': get_account(19), 'value': amount_in_wei(PUBSALES_FLOAT_VAL*3)})
    contract.mint(2,{'from': get_account(14), 'value': amount_in_wei(PUBSALES_FLOAT_VAL*2)})
    contract.mint(2,{'from': get_account(15), 'value': amount_in_wei(PUBSALES_FLOAT_VAL*2)})
    contract.mint(2,{'from': get_account(8), 'value': amount_in_wei(PUBSALES_FLOAT_VAL*2)})
    contract.mint(2,{'from': get_account(5), 'value': amount_in_wei(PUBSALES_FLOAT_VAL*2)})
    contract.mint(2,{'from': get_account(7), 'value': amount_in_wei(PUBSALES_FLOAT_VAL*2)})
    
    assert(contract.ownerOf(161) == get_account(6))
    assert(contract.ownerOf(162) == get_account(6))
    assert(contract.ownerOf(163) == get_account(6))
    
    assert(contract.ownerOf(173) == get_account(12))
    assert(contract.ownerOf(174) == get_account(12))
    assert(contract.ownerOf(175) == get_account(12))
    
    assert(contract.ownerOf(176) == get_account(13))
    assert(contract.ownerOf(177) == get_account(13))
    assert(contract.ownerOf(178) == get_account(13))
    
    # register team of 8 
    register_teams(contract,"wonderful", 
        [get_account(6),[161,162,163],
        get_account(12),[173,175],
        get_account(13),[176,177,178],
        get_account(17),[182,183]])

    register_teams(contract,"locos",
    [get_account(16),[179],
     get_account(18),[185],
     get_account(19),[189],
     get_account(14),[192]])
    
    third_prize_sent(contract,get_account(1), get_account(6), get_account(12),False)

#@pytest.mark.skip(reason="focus")
def test_burn_tokens_th_calc(contract):
    if network.show_active() not in ["development"] or "fork" in network.show_active():
        pytest.skip("Only for local testing")

    th_balance = contract.reservedTHPrize()

    setMaxDrop(contract,400,3)
    
    finish_presales(contract)

    # mint 10% (40)
    contract.mint(10,{'from': get_account(14), 'value': amount_in_wei(PUBSALES_FLOAT_VAL*10)})
    contract.mint(10,{'from': get_account(15), 'value': amount_in_wei(PUBSALES_FLOAT_VAL*10)})
    contract.mint(10,{'from': get_account(16), 'value': amount_in_wei(PUBSALES_FLOAT_VAL*10)})
    contract.mint(10,{'from': get_account(17), 'value': amount_in_wei(PUBSALES_FLOAT_VAL*10)})

    # Cannot set the new MaxDrop below already issued amount
    with brownie.reverts("dev: cannot set maxDrop below already supply"):
        contract.setMaxDrop(10)

    # Reduce maxDrop to 40
    contract.setMaxDrop(40)

    assert(contract.getMaxDrop() == 40)

    # This means 100% has been dropped  
    # Let's confirm TH is expected one  
    assert contract.reservedTHPrize() == th_balance + Wei("50 ether")        

    # let's try just an additional one to get SOLD OUT message  
    with brownie.reverts("dev: SOLD OUT!"):
        contract.mint(1,{'from': get_account(11), 'value': amount_in_wei(PUBSALES_FLOAT_VAL)})
