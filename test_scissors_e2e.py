# 
# (c) 2022, rpsnft.art
#

import pytest
import brownie

from decimal import *
from brownie import accounts, network, Scissors, Wei, exceptions, convert 
from scripts.helpful_scripts import get_account
from scripts.helpful_tests import create_contract,complete_e2e_test

# Test E2E with following amounts:
# pre-sales 10 tokens
# public sales 990 tokens
# expected total sales: 1000 * 0,055 = 55 eth

# Set the test environment at module level for all tests below
@pytest.fixture(scope="module", autouse=True)
def contract():
    return create_contract()

# After setting up module baseline (previous function) for fixtures
# we define the isolation level of the fixture for function (ie every test 
# function will keep previous status setup at module level as the baseline) 
#@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass

#@pytest.mark.skip(reason="focus")
def test_e2e_unit_test(contract):
    if network.show_active() not in ["development"] or "fork" in network.show_active():
        pytest.skip("Only for local testing")
    
    complete_e2e_test(contract,39,15,1,275,1120,25,120,55)
