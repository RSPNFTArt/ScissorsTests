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

# TODO: Update with real 275 and 10000 and last 275 to fail
#@pytest.mark.skip(reason="focus")
def test_e2e_real_unit_test(contract):
    if network.show_active() not in ["development"] or "fork" in network.show_active():
        pytest.skip("Only for local testing")
    
    # 541.75 = 550 (0.055x10000 - 0.055x150 free)
    complete_e2e_test(contract,390,9,10,275,10000,25,150,541.75)
