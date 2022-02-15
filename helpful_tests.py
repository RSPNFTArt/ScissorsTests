from cmath import phase
from turtle import pu
import pytest
import brownie
from brownie import Wei,convert,accounts,config,network,Scissors
from scripts.helpful_scripts import get_account,amount_in_eths,account_in_eths,eths_r_equal,amount_in_wei

PRESALES_FLOAT_VAL = 0.055
PUBSALES_FLOAT_VAL = 0.070

PRESALES_MINT_PRICE = "0.055 ether"
PUBSALES_MINT_PRICE = "0.070 ether"

def create_contract():
    scissor = Scissors.deploy({"from": get_account(0)})    
    scissor.setPrizesAccounts(get_account(30),get_account(31))
    scissor.chargeContract({'from': get_account(4), 'value': Wei("70 ether")})
    scissor.unpause()
    scissor.setBaseURI("https://ipfs.io/ipfs/")
    return scissor

def setMaxDrop(contract,_maxDrop,_preSales=25,_whiteList=150):
    
    # if whitelist size is bigger than both _maxdrop and _presales is that we are not 
    # interested in testing now whitelist properly and just having 10 is enough 
    if (_maxDrop + _preSales) < _whiteList :        
        contract.setMaxDrop(_preSales,_maxDrop,1)
    else:
        contract.setMaxDrop(_preSales,_maxDrop,_whiteList)

def init_presales(contract):
    assert(not contract.inPresales())
   
    # Simulate presales
    contract.preSalesOn()

    assert(contract.inPresales())
   
def finish_presales(contract):
    assert(not contract.inPublicSales())

    # disable preSales mode
    contract.preSalesOff()

    # we need to complete presales before we can start minting in public sales
    contract.preSalesComplete()
    assert(contract.preSalesFinished())
    assert(not contract.inPresales())
    assert(not contract.inPublicSales())

    # preSalesComplete pauses contract before Public Sales starts
    contract.unpause()

    assert(contract.inPublicSales())

def get_founder_accts(contract):
    # Set founder accounts
    ss = get_account(32) # Scissors account
    rb = get_account(33) # Rock account
    pj = get_account(34) # Paper account
    rl = get_account(35) # Lizard account
    sp = get_account(36) # Spok account
    ngo = get_account(37) # NGO account
    mk = get_account(38) # Marketing account 
    do = get_account(39) # Dream On account

    contract.setFounderAddresses(ss,rb,pj,rl,sp,ngo,mk,do)

    return (ss,rb,pj,rl,sp,ngo,mk,do)

def get_founder_balance(ss,rb,pj,rl,sp,ngo,mk,do):
     # Get founders' balances
    ss_balance = ss.balance()
    rb_balance = rb.balance()
    pj_balance = pj.balance()
    rl_balance = rl.balance()
    sp_balance = sp.balance()
    ngo_balance = ngo.balance()
    mk_balance = mk.balance()
    do_balance = do.balance()

    return (ss_balance,rb_balance,pj_balance,rl_balance,sp_balance,ngo_balance,mk_balance,do_balance)

def withdrawn_checks(contract,max_balance,vip_tokens,current_balance,previous_balance,
                         accs_vip,mult_vip_expected):
        
    # Calc expected stakes
    cofounder_stk = max_balance/100*16
    vip_stk = cofounder_stk/len(vip_tokens)
    five_pct_stk = max_balance/100*5
    
    # Confirm withdrawing (remaining keeps in owner account)
    assert eths_r_equal(current_balance[0] , previous_balance[0] + convert.to_uint(cofounder_stk))
    assert eths_r_equal(current_balance[1] , previous_balance[1] + convert.to_uint(cofounder_stk))
    assert eths_r_equal(current_balance[2] , previous_balance[2] + convert.to_uint(cofounder_stk))
    assert eths_r_equal(current_balance[3] , previous_balance[3] + convert.to_uint(cofounder_stk))    
    assert eths_r_equal(current_balance[4] , previous_balance[4] + convert.to_uint(five_pct_stk))
    assert eths_r_equal(current_balance[5] , previous_balance[5] + convert.to_uint(five_pct_stk))
    assert eths_r_equal(current_balance[6] , previous_balance[6] + convert.to_uint(five_pct_stk))
    assert eths_r_equal(current_balance[7] , previous_balance[7] + convert.to_uint(five_pct_stk))

    # Let's now check pull payments in this contract

    vip_cur_balance=[]
    vip_expected=[]

    # check payments correspond to winners position
    for i in range(0,len(accs_vip)):
        # Calc the expected amount as per each account participation 
        expected = mult_vip_expected[i]*vip_stk
        vip_expected.append(expected)

        assert eths_r_equal(contract.payments(get_account(accs_vip[i])), expected)

        # get current balances
        vip_cur_balance.append(get_account(accs_vip[i]).balance())    
    
    # Verify payments can be pulled by VIPs
    for acc in accs_vip:
        contract.withdrawPayments(get_account(acc),{'from': get_account(acc)})
 
    # balances should increase as per expected withdrawn per co-cofounder
    for i in range(0,len(accs_vip)):
        assert (account_in_eths(accs_vip[i])) == amount_in_eths(vip_cur_balance[i] + vip_expected[i])

    # check payments correspond to winners position
    for acc in accs_vip:
        assert contract.payments(get_account(acc)) == 0

# _whiteListMintAmount should be min 10
def whitelist(contract, _whiteListMintAmount):

    if _whiteListMintAmount < 10:
        raise("_whiteListMintAmount: Amount should be at least 10 or more")
    supply = contract.totalSupply()

    # owner mint is everything else -10
    ownerMint = _whiteListMintAmount - 10

    # Calc groups of 50 to mint during initial mint
    numGroupsOf50 = ownerMint // 50
    tokensRemaining = ownerMint % 50

    # try to exceed the max amount in 1 to get error
    with brownie.reverts("dev: the initial amount is exceeded"):
        contract.initialMint(_whiteListMintAmount + 1, {'from': get_account(0)})

    expectedPartial = 0
    # Initial mint of one part 
    # part to be minted by whitelist owners = 10 (next section)
    if numGroupsOf50 > 1:
        contract.initialMint(50,{'from': get_account(0)})
        numGroupsOf50 -= 1
        expectedPartial += 50
    
    # Mint 10
    contract.addToWhiteList([get_account(40),get_account(41),get_account(42)],{'from': get_account(0)})

    with brownie.reverts("dev: Total amount exceeded for white-listed wallet"):
        contract.whiteListMint(30,{"from":get_account(40)})

    # Whitelist Owners minting - 10 mints
    contract.whiteListMint(3,{"from":get_account(40)})
    contract.whiteListMint(2,{"from":get_account(40)})

    with brownie.reverts("dev: Total amount exceeded for white-listed wallet"):
        contract.whiteListMint(1,{"from":get_account(40)})

    contract.addToWhiteList([get_account(44)])
    contract.whiteListMint(4,{"from":get_account(44)})
    with brownie.reverts("dev: Total amount exceeded for white-listed wallet"):
        contract.whiteListMint(2,{"from":get_account(44)})

    contract.whiteListMint(1,{"from":get_account(44)})

    with brownie.reverts("dev: Total amount exceeded for white-listed wallet"):
        contract.whiteListMint(1,{"from":get_account(44)})

    expectedPartial += 10

    assert(contract.totalSupply() == supply + expectedPartial)

    # Mint the rest in chunks of 50 max (to avoid gas limits)
    for i in range(numGroupsOf50):
        contract.initialMint(50)

    if tokensRemaining > 0:
        contract.initialMint(tokensRemaining)

    assert(contract.totalSupply() == supply + _whiteListMintAmount)

    with brownie.reverts("dev: initial amount already allocated"):
        contract.initialMint(1)

    with brownie.reverts("dev: initial amount already allocated"):
        contract.whiteListMint(1,{"from":get_account(41)})

# 
# _range_390 = 390
# _range_24 = 24
# _range_10 = 10
# _maxDrop = 10000
# _expected_total_eths = 550
#
def complete_e2e_test(contract,_range_390,_range_24,_range_10,_maxPreSales,_maxDrop,
                      _maxNFTPerAcct,_whiteListMintAmount,
                      _expected_total_eths):
        
    # Set founder accounts
    (ss,rb,pj,rl,sp,ngo,mk,do) = get_founder_accts(contract)

    # Get founders' balances
    (ss_balance,rb_balance,pj_balance,rl_balance,sp_balance,ngo_balance,mk_balance,do_balance) = \
        get_founder_balance(ss,rb,pj,rl,sp,ngo,mk,do)

    # Get contract balance
    last_balance = contract.balance()

    setMaxDrop(contract,_maxDrop,_maxPreSales,_whiteListMintAmount) 

    # set max per tx limit
    contract.setMaxSalesNFTAmount(_maxNFTPerAcct)

    init_presales(contract)
    
    # add test accounts to the pre-sale list
    contract.addToPresalesList([get_account(3),get_account(4),get_account(7)],{'from': get_account(0)})
    
    # break it in two to allow adding later 
    contract.addToPresalesList([get_account(8),get_account(9),get_account(10)],{'from': get_account(0)})
    
    # th_balance is the reserved prize so far
    th_balance = contract.reservedTHPrize()

    # presales is just 10 (not yet 25%)
    contract.preSalesMint(2,{'from': get_account(3), 'value': amount_in_wei(PRESALES_FLOAT_VAL*2)})
    contract.preSalesMint(2,{'from': get_account(4), 'value': amount_in_wei(PRESALES_FLOAT_VAL*2)})
    contract.preSalesMint(2,{'from': get_account(8), 'value': amount_in_wei(PRESALES_FLOAT_VAL*2)})
    contract.preSalesMint(2,{'from': get_account(9), 'value': amount_in_wei(PRESALES_FLOAT_VAL*2)})
    contract.preSalesMint(2,{'from': get_account(10), 'value': amount_in_wei(PRESALES_FLOAT_VAL*2)})

    # TH balance should be the same as we have not pass the 25% of max (5 = 20/4)
    assert th_balance == 0
    assert contract.balance() == last_balance + amount_in_wei(PRESALES_FLOAT_VAL*10)
    
    finish_presales(contract)

    # allow whitelist (-150: _whiteListMintAmount)
    # During real execution we would run whitelist before presales but tests accounts 
    # but we can run it anytime and current tests are based on accounts from pre-sales
    # so to avoid affecting the expected results we move this after presales are finished
    whitelist(contract,_whiteListMintAmount)

    # Let's keep to check no variance in supply
    supply = contract.totalSupply()

    # supply = 150 (_whiteListMintAmount) + 10 (presales minted above)
    assert supply == _whiteListMintAmount + 10 

    # We have pre-minted 10 , remaining 
    # Let's now mint up to 100% (390 times 5 each account)
    for i in range(_range_390): 
        contract.mint(5,{'from': get_account(3), 'value': amount_in_wei(PUBSALES_FLOAT_VAL*5)})
        contract.mint(5,{'from': get_account(4), 'value': amount_in_wei(PUBSALES_FLOAT_VAL*5)})
        contract.mint(5,{'from': get_account(8), 'value': amount_in_wei(PUBSALES_FLOAT_VAL*5)})
        contract.mint(5,{'from': get_account(9), 'value': amount_in_wei(PUBSALES_FLOAT_VAL*5)})
        contract.mint(5,{'from': get_account(10), 'value': amount_in_wei(PUBSALES_FLOAT_VAL*5)})

    # 390 veces 25 es 9750, que a los 10 de presales nos da 9760, quedan 240 (-150 de whitelist)
    # para llegar a 10K
    _cost_range_10=_range_10*PUBSALES_FLOAT_VAL
    
    # restamos 15 porque vamos de 10 en 10
    for i in range(_range_24):
        contract.mint(_range_10,{'from': get_account(10), 'value': amount_in_wei(_cost_range_10)})
    
    print(f"TotalSupply = {contract.totalSupply()} and _maxDrop = {_maxDrop}")

    # Let's confirm supply is the expected one 10K
    assert contract.totalSupply() == _maxDrop
    
    # let's try just an additional one to get SOLD OUT message  
    with brownie.reverts("dev: SOLD OUT!"):
        contract.mint(1,{'from': get_account(11), 'value': amount_in_wei(PUBSALES_FLOAT_VAL)})

    # refresh supply for next assert
    supply = contract.totalSupply()

    # Let's confirm TH is expected one  
    assert contract.reservedTHPrize() == Wei("50 ether")        
    exp = Wei(f"{_expected_total_eths} ether") - Wei("9 ether")
    
    # Confirm contract balance
    # expected amount (exp) - 50 ETH from treasure hunt pot - 9 ETH from 1st+2nd prize (4+5)
    assert contract.balance() == last_balance + exp
    
    # Assign new last_balance for contract
    last_balance = contract.balance()

    # set tokens for VIPs
    vip_tokens = [1,3,5,7,9] # from pre-sales
    contract.setVIPTokens(vip_tokens)

    # Get maximum to withdraw based on TH parts released
    max_balance = contract.maxBalanceToWithdraw()
  
    # Request withdrawing
    contract.withdraw({'from': get_account(0)})

    # Calc expected stakes
    current_balance = [ss.balance(),rb.balance(),pj.balance(),
                       rl.balance(),sp.balance(),ngo.balance(),
                       mk.balance(), do.balance()]
    previous_balance = [ss_balance,rb_balance,pj_balance,
                        rl_balance, sp_balance, ngo_balance,
                        mk_balance, do_balance]
    accs_vip = [3,4,8,9,10]
    mult_vip_expected = [1,1,1,1,1]
    withdrawn_checks(contract,max_balance,vip_tokens,current_balance,previous_balance,
                         accs_vip,
                         mult_vip_expected) 

    # PRIZES     
    contract.setSecret(0xc400cda91a2ade601f638972b9ff78851ab8e8bef801f0fe79680d215190cca0)

    first_prize_sent(contract)

    second_prize_sent(contract)

    # Starting index to register teams
    # starting here first 5 tokens are for account 3, then next 5 for account 4,
    # subsequent accounts are 8 , 9 , 10
    indx = _whiteListMintAmount + 10

    # register winner team of 8 
    register_teams(contract,"wonderful", 
        [get_account(3),[indx+1,indx+2,indx+3],
        get_account(4),[indx+6,indx+8],
        get_account(8),[indx+11,indx+12,indx+13],
        get_account(9),[indx+16,indx+17]])
    
    third_prize_sent(contract,get_account(1), get_account(3), get_account(8))
    
def first_prize_sent(contract,owner_calls=True):
    
    contract.chargeContract({'from': get_account(2), 'value': contract.FIRST_PRIZE_TOTAL_ETH_AMOUNT()})

    winners = [get_account(11), get_account(12), get_account(13)]
    non_winners = [get_account(18), get_account(19), get_account(20)]

    # Add payments to 3 accounts
    contract.sendGiveAway(1, winners)
    
    # check payments correspond to winners position
    assert contract.payments(winners[0]) == contract.FIRST_PRIZE_FIRST_ETH_AMOUNT()
    assert contract.payments(winners[1]) == contract.FIRST_PRIZE_SECOND_ETH_AMOUNT()
    assert contract.payments(winners[2]) == contract.FIRST_PRIZE_THIRD_ETH_AMOUNT()

    # get current balances
    winner_1_balance = winners[0].balance()
    winner_2_balance = winners[1].balance()
    winner_3_balance = winners[2].balance()
        
    if owner_calls:

        # Verify payments can be pulled by winners
        contract.withdrawPayments(winners[0],{'from': winners[0]})
        contract.withdrawPayments(winners[1],{'from': winners[1]})
        contract.withdrawPayments(winners[2],{'from': winners[2]})

        # balances should increase as per prizes under contract 
        # Scissors.FIRST_PRIZE_FIRST_ETH_AMOUNT 
        # Scissors.FIRST_PRIZE_SECOND_ETH_AMOUNT
        # Scissors.FIRST_PRIZE_THIRD_ETH_AMOUNT
        assert winners[0].balance() == winner_1_balance + contract.FIRST_PRIZE_FIRST_ETH_AMOUNT() 
        assert winners[1].balance() == winner_2_balance + contract.FIRST_PRIZE_SECOND_ETH_AMOUNT()
        assert winners[2].balance() == winner_3_balance + contract.FIRST_PRIZE_THIRD_ETH_AMOUNT()

    else:
        non_winner_0_balance = non_winners[0].balance()
        non_winner_1_balance = non_winners[1].balance()
        non_winner_2_balance = non_winners[2].balance()

        # Verify payments cannot be pulled by wrong winners
        contract.withdrawPayments(winners[0],{'from': non_winners[0]})
        assert non_winners[0].balance() == non_winner_0_balance
        assert winners[0].balance() == winner_1_balance + contract.FIRST_PRIZE_FIRST_ETH_AMOUNT()

        # Verify payments cannot be pulled by wrong winners
        contract.withdrawPayments(winners[1],{'from': non_winners[1]})
        assert non_winners[1].balance() == non_winner_1_balance
        assert winners[1].balance() == winner_2_balance + contract.FIRST_PRIZE_SECOND_ETH_AMOUNT()

        # Verify payments cannot be pulled by wrong winners
        contract.withdrawPayments(winners[2],{'from': non_winners[2]})
        assert non_winners[2].balance() == non_winner_2_balance
        assert winners[2].balance() == winner_3_balance + contract.FIRST_PRIZE_THIRD_ETH_AMOUNT()

    # check payments correspond to winners position
    assert contract.payments(winners[0]) == 0
    assert contract.payments(winners[1]) == 0
    assert contract.payments(winners[2]) == 0

    # Cannot release first prize twice 
    with brownie.reverts("dev: 1st prize already released"):
        contract.sendGiveAway(1, winners)
    
    # Verify payments cannot be pulled twice
    contract.withdrawPayments(winners[0],{'from': winners[0]})
    contract.withdrawPayments(winners[1],{'from': winners[1]})
    contract.withdrawPayments(winners[2],{'from': winners[2]})

    assert winners[0].balance() == winner_1_balance + contract.FIRST_PRIZE_FIRST_ETH_AMOUNT() 
    assert winners[1].balance() == winner_2_balance + contract.FIRST_PRIZE_SECOND_ETH_AMOUNT()
    assert winners[2].balance() == winner_3_balance + contract.FIRST_PRIZE_THIRD_ETH_AMOUNT()

    # check payments correspond to winners position
    assert contract.payments(winners[0]) == 0
    assert contract.payments(winners[1]) == 0
    assert contract.payments(winners[2]) == 0

def second_prize_sent(contract,owner_calls=True):
    
    contract.chargeContract({'from': get_account(2), 'value': f"{contract.SECOND_PRIZE_TOTAL_ETH_AMOUNT()}"})

    dummy_winners = []

    # Add payments to 10 random accounts among the 12 particpated
    contract.sendGiveAway(2,dummy_winners)
    
    # get the list of winners
    winners = contract.second_prize_winners

    # Check payments for winners are the ones in the second prize
    # >= as same owner may win more than once
    for i in range(0,10):
        assert contract.payments(winners(i)) >= contract.SECOND_PRIZE_PER_WALLET_ETH_AMOUNT() 

    if not owner_calls:
        non_winner_index = -1

        # Search for the index 
        current_net = network.show_active()
        # this does not work ->
        #    max_accs = config['networks'][current_net]['cmd_settings']['accounts']
        max_accs = 30
        
        non_winner_acc = None
        
        ## Search for non-winner account

        found = True
        
        for i in range(0,max_accs):
            
            if not found:
                break
            
            found=False

            for j in range(0,10):
                if accounts[i]==winners(j):
                    found = True
                    break                

            if not found:                        
                non_winner_acc = accounts[i]
        
        # Crash if no index found
        assert non_winner_acc != None

        #non_winner_acc = get_account(non_winner_index)
        nonWinnerAccBalance = non_winner_acc.balance()

        # check balances prev and post payment withdrawn 
        for i in range(0,10):
            accountWin = accounts.at(winners(i),force=True)
            winner_prev_balance = accountWin.balance()
            non_winner_prev_balance = non_winner_acc.balance()
            contract.withdrawPayments(accountWin, {'from': non_winner_acc}) 
            assert accountWin.balance() == winner_prev_balance + contract.SECOND_PRIZE_PER_WALLET_ETH_AMOUNT()
            assert non_winner_acc.balance() == non_winner_prev_balance

        # balance of non winner account should be the same after withdrawing 
        assert non_winner_acc.balance() == nonWinnerAccBalance
        
    else:        
        hwinner = {}
        # check balances prev and post payment withdrawn 
        for i in range(0,10):
            # get keys
            lh = list(hwinner)

            if not winners(i) in lh:
                # Add to hash to avoid checking again
                hwinner[winners(i)]=True

                accountWin = accounts.at(winners(i),force=True)
                winner_prev_balance = accountWin.balance()
                contract.withdrawPayments(accountWin, {'from': accountWin})                 
                assert accountWin.balance() >= (winner_prev_balance + contract.SECOND_PRIZE_PER_WALLET_ETH_AMOUNT())
    
    # Check no debt left after withdrawn
    for i in range(0,10):
        accountWin = accounts.at(winners(i),force=True)
        assert contract.payments(accountWin) == 0    

    with brownie.reverts("dev: 2nd prize already released"):
        contract.sendGiveAway(2, [])

def register_teams(contract,team,params):
    
    with brownie.reverts("tokens list size exceed maximum to create list"):
        contract.registerTHTeam("locos", [1,2,3,4,5,6,7,8,9,10,11]) 

    with brownie.reverts("tokens list size exceed maximum to create list"):
        contract.registerTHTeam("locos", [1,2,3,4,5,6,7,8,9,10]) 

    tx = contract.registerTHTeam(team, params[1], { 'from': params[0] }) 
    ret = tx.return_value
    print(f"contract.registerTHTeam = {ret}")

    tx = contract.joinTHTeam(team, params[3], { 'from': params[2] }) 
    ret = tx.return_value
    print(f"contract.joinTHTeam #1 = {ret}")
    
    tx = contract.joinTHTeam(team, params[5], { 'from': params[4] }) 
    ret = tx.return_value
    print(f"contract.joinTHTeam #2 = {ret}")

    tx = contract.joinTHTeam(team, params[7], { 'from': params[6] }) 
    ret = tx.return_value
    print(f"contract.joinTHTeam #3 = {ret}")
    
    with brownie.reverts("team name already taken"):
        contract.registerTHTeam(team, [1,2,3,4,5,6,7,8,9])

def third_prize_sent(contract,not_registred_acct,first_acct,second_acct,owner_calls=True):

    # Set founder accounts
    (ss,rb,pj,rl,sp,ngo,mk,do) = get_founder_accts(contract)
    
    # Check balance from contract
    payingAccBalance = contract.balance() 
    
    # not registered
    with brownie.reverts("caller not registered in any team"):
        contract.decryptForTHPrize("lolo",{'from': not_registred_acct}) # get_account(1)

    # wrong sentence
    with brownie.reverts("RPS - Wrong, keep trying."):
        contract.decryptForTHPrize("lolo",{'from': first_acct}) # get_account(6)

    # write sentence
    contract.decryptForTHPrize("me gustan las galletas y el pollo",{'from': second_acct}) # get_account(12)
 
    # prize already released
    with brownie.reverts("dev: 3rd prize already released"):
        contract.decryptForTHPrize("me gustan las galletas y el pollo",{'from': first_acct})

    # prize already released
    with brownie.reverts("dev: 3rd prize already released"):
        contract.decryptForTHPrize("xyz",{'from': first_acct})

    last_ngo_bal = ngo.balance()
    print(f"Last NGO Balance = {last_ngo_bal}")

    #contract.sendRemainderToNGO()
    #new_ngo_bal = ngoAddr.balance()
    #print(f"New NGO Balance = {new_ngo_bal}")
    #print(f"NGO Diff = {new_ngo_bal - last_ngo_bal}")

    print(f"Prizes balance = {contract.balance()}")
    print(f"payingAccBalance = {payingAccBalance}")
    print(f"Diff Prizes.Balance = {payingAccBalance - contract.balance()}")
    assert contract.balance() == payingAccBalance - Wei("50 ether")

    # Check the name of the TH winner team
    assert contract.getTHTeamName() == "wonderful"
    
    # Get the list of addresses
    th_winners = contract.getTHWinnerAddrs()
    
    # Check payments for winners are the ones in the second prize
    for _ethAddr in th_winners:
        _acct = accounts.at(_ethAddr)
        print(f"Acct = {_acct} , with pending payment of {contract.payments(_acct)} is == {contract.TH_PRIZE_PER_WALLET() * th_winners.count(_acct) } ?")
        assert contract.payments(_acct) == contract.TH_PRIZE_PER_WALLET() * th_winners.count(_acct)

    # get array of unique elements 
    prev_balance_winners = list(set(th_winners))
    
    # create and fill hashmap with previous amounts in balance
    hprev_balance_winners = {}
    
    for _ethAddr in prev_balance_winners:
        _acct = accounts.at(_ethAddr)
        hprev_balance_winners[_acct] = _acct.balance()

    # check balances prev and post payment withdrawn 
    for _ethAddr in th_winners: 
        accountWin = accounts.at(_ethAddr)       
                
        if not owner_calls:            
            non_winner_prev_balance = get_account(1).balance()
            contract.withdrawPayments(accountWin, {'from': get_account(1)}) 
            assert get_account(1).balance() == non_winner_prev_balance
        else:            
            contract.withdrawPayments(accountWin, {'from': accountWin}) 
            
        # check if previous account balance has grown with new amount
        assert accountWin.balance() == hprev_balance_winners[accountWin] + (contract.TH_PRIZE_PER_WALLET() * th_winners.count(accountWin))

    # Check no debt left after withdrawn
    for _ethAddr in th_winners:
        _acct = accounts.at(_ethAddr)
        assert contract.payments(_acct) == 0

def no_1st_n_2nd_prizes_yet(first_prize_acct_balance, second_prize_acct_balance):
    # No changes in 1st prize acct yet
    assert get_account(30).balance() == first_prize_acct_balance 

    # No changes in 2nd prize acct yet
    assert get_account(31).balance() == second_prize_acct_balance

def set_baseline_4_prizes(contract):

    # Let's keep to check variance in supply
    supply = contract.totalSupply()

    # Get contract balance
    last_balance = contract.balance()

    # th_balance is the reserved prize so far
    th_balance = contract.reservedTHPrize()

    # Account 30 is the 1st prize account
    first_prize_acct_balance = get_account(30).balance()

    # Account 30 is the 1st prize account
    second_prize_acct_balance = get_account(31).balance()

    return (supply,last_balance,th_balance,first_prize_acct_balance,second_prize_acct_balance)

# Assumption is maxdrop has been set to 20
def pct_at_25(contract,max):
    
    assert contract.getMaxDrop() == max

    (supply, last_balance, th_balance, first_prize_acct_balance, second_prize_acct_balance) = \
        set_baseline_4_prizes(contract)

    # Let's confirm no previous supply
    assert supply == 0

    init_presales(contract)
    
     # add test accounts to the pre-sale list
    contract.addToPresalesList([get_account(5),get_account(6)],{'from': get_account(0)})
    
    # presales is just 3 (not yet 25%)
    contract.preSalesMint(2,{'from': get_account(6), 'value': amount_in_wei(PRESALES_FLOAT_VAL*2)})
    contract.preSalesMint(1,{'from': get_account(5), 'value': amount_in_wei(PRESALES_FLOAT_VAL)})
    
    presales_in_contract = amount_in_wei(PRESALES_FLOAT_VAL*3)
    assert contract.balance() == last_balance + presales_in_contract

    # TH balance should be the same as we have not pass the 25% of max (5 = 20/4)
    assert contract.reservedTHPrize() == th_balance 
    assert contract.reservedTHPrize() == 0

    finish_presales(contract)

    amount_to_mint = (max/4) - 3
    price = amount_to_mint * PUBSALES_FLOAT_VAL
    
    pubsales_in_contract = amount_in_wei(price)

    # Let's now mint up to 25% (up to max/4) 
    contract.mint(amount_to_mint,{'from': get_account(3), 'value': amount_in_wei(price)})
    
    # Let's keep to check variance in supply
    supply = contract.totalSupply()

    # Let's confirm supply it is expected 5 (25% of maxDrop of 20)
    assert supply == max/4

    # Let's confirm 25% give away of +5 ETH has been granted in TH account
    assert contract.reservedTHPrize() == th_balance + Wei("5 ether")        

    # no prizes yet
    no_1st_n_2nd_prizes_yet(first_prize_acct_balance, second_prize_acct_balance)    
    
    # In 25% the contract is still keeping 4 ethers of 1st price until 50% has been achieved
    assert contract.balance() == last_balance + presales_in_contract + pubsales_in_contract
    assert contract.reservedTHPrize() == Wei("5 ether")

# Assumption is maxdrop has been set to 20
def pct_at_50(contract,max):

    assert contract.getMaxDrop() == max
    
    (supply, last_balance, th_balance, first_prize_acct_balance, second_prize_acct_balance) = \
        set_baseline_4_prizes(contract)

    # Let's confirm previous supply is expected 25% (5 of maxDrop of 20)
    assert supply == max/4    

    amount_to_mint = (max/4) - 1
    price = amount_to_mint * PUBSALES_FLOAT_VAL
    pubsales_in_contract = amount_in_wei(price)

    # Let's now mint below 50% (up to max/2 - 1 of max) 
    contract.mint(amount_to_mint,{'from': get_account(8), 'value': amount_in_wei(price)})
    
    # No change in TH yet
    assert contract.reservedTHPrize() == th_balance
    assert contract.reservedTHPrize() == Wei("5 ether")

    # no prizes yet
    no_1st_n_2nd_prizes_yet(first_prize_acct_balance, second_prize_acct_balance)

    # Confirm contract balance
    assert contract.balance() == last_balance + amount_in_wei(price)

    # Let's now mint up to 50% (up to max/2 of max) 
    contract.mint(1,{'from': get_account(8), 'value': amount_in_wei(PUBSALES_FLOAT_VAL)})
    pubsales_in_contract+=amount_in_wei(PUBSALES_FLOAT_VAL)

    # Let's confirm supply is the expected one (max/4) of maxDrop of max)
    assert contract.totalSupply() == supply + (max/4)

    # Let's confirm 50% give away of +10 ETH has been granted in TH account
    assert contract.reservedTHPrize() == th_balance + Wei("10 ether")       

    # Let's confirm 1st prize is reserved
    assert get_account(30).balance() == first_prize_acct_balance + Wei("4 ether")

    # No changes in 2nd prize acct yet
    assert get_account(31).balance() == second_prize_acct_balance
            
    # Confirm contract balance
    assert contract.balance() == last_balance + pubsales_in_contract - Wei("4 ether")
    assert contract.reservedTHPrize() == Wei("15 ether")

# Assumption is maxdrop has been set to 20
def pct_at_75(contract,max):
    
    assert contract.getMaxDrop() == max

    (supply, last_balance, th_balance, first_prize_acct_balance, second_prize_acct_balance) = \
        set_baseline_4_prizes(contract)

    # Let's confirm previous supply is expected 50% (10 of maxDrop of 20)
    assert supply == max/2

    amount_to_mint = (max/4) - 1
    price = amount_to_mint * PUBSALES_FLOAT_VAL
    pubsales_in_contract = amount_in_wei(price)

    # Let's now mint below to 75% 
    contract.mint(amount_to_mint,{'from': get_account(3), 'value': amount_in_wei(price)})

    # No change in TH yet
    assert contract.reservedTHPrize() == th_balance
    assert contract.reservedTHPrize() == Wei("15 ether")

    # No change in 2nd prize yet
    assert get_account(31).balance() == second_prize_acct_balance

    # Confirm contract balance (30 ether from TH and 9 ether from 1st+2nd prize)
    assert contract.balance() == last_balance + amount_in_wei(price)

    # Let's now mint up to 75% 
    contract.mint(1,{'from': get_account(3), 'value': amount_in_wei(PUBSALES_FLOAT_VAL)})
    pubsales_in_contract += amount_in_wei(PUBSALES_FLOAT_VAL)

    # Let's confirm supply is the expected one (+1 of maxDrop of 20)
    assert contract.totalSupply() == supply + (max/4)

    # Let's confirm 50% give away of +10 ETH has been granted in TH account
    assert contract.reservedTHPrize() == th_balance + Wei("15 ether")        

    # Let's confirm first prize is reserved
    assert get_account(30).balance() == first_prize_acct_balance

    # Let's confirm first prize is reserved
    assert get_account(31).balance() == second_prize_acct_balance + Wei("5 ether")

    # Confirm contract balance (30 ether from TH and 9 ether from 1st+2nd prize)
    assert contract.balance() == last_balance + pubsales_in_contract - Wei("5 ether")
    assert contract.reservedTHPrize() == Wei("30 ether")

def pct_at_100(contract,max):

    (supply, last_balance, th_balance, first_prize_acct_balance, second_prize_acct_balance) = \
        set_baseline_4_prizes(contract)

    # Let's confirm previous supply is expected 75% (15 of maxDrop of 20)
    assert supply == max*3/4

    amount_to_mint = (max/4) - 1
    price = amount_to_mint * PUBSALES_FLOAT_VAL
    pubsales_in_contract = amount_in_wei(price)

    # Let's now mint below 100% (19 of 20) 
    contract.mint(amount_to_mint,{'from': get_account(9), 'value': amount_in_wei(price)})

    # Let's confirm 50% give away of +10 ETH has been granted in TH account
    assert contract.reservedTHPrize() == th_balance
    assert contract.reservedTHPrize() == Wei("30 ether")

    # Confirm contract balance
    assert contract.balance() == last_balance + amount_in_wei(price)

    # Let's now mint up to 100% (up to 20) 
    contract.mint(1,{'from': get_account(9), 'value': amount_in_wei(PUBSALES_FLOAT_VAL)})
    pubsales_in_contract += amount_in_wei(PUBSALES_FLOAT_VAL)

    # Let's confirm first prize is reserved
    assert get_account(30).balance() == first_prize_acct_balance

    # Let's confirm first prize is reserved
    assert get_account(31).balance() == second_prize_acct_balance 

    # Let's confirm supply is the expected one (+5 of maxDrop of 20)
    assert contract.totalSupply() == supply + (max/4)

    # Let's confirm 50% give away of +10 ETH has been granted in TH account
    assert contract.reservedTHPrize() == th_balance + Wei("20 ether")        

    # Confirm contract balance
    assert contract.balance() == last_balance + pubsales_in_contract
    assert contract.reservedTHPrize() == Wei("50 ether")

def mint_everything(contract,max):
    # mint up to 25%
    pct_at_25(contract,max)

    # mint up to 50%
    pct_at_50(contract,max)

    # mint up to 75%
    pct_at_75(contract,max)

    # mint up to 100%
    pct_at_100(contract,max)

