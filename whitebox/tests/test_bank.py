"""White-box tests for bank state transitions and edge cases."""

import pytest

from moneypoly.bank import Bank
from moneypoly.config import BANK_STARTING_FUNDS, STARTING_BALANCE
from moneypoly.player import Player


def test_collect_and_pay_out_update_bank_balance():
    """The bank should track inbound and outbound cash movement."""
    bank = Bank()

    bank.collect(125)

    assert bank.get_balance() == BANK_STARTING_FUNDS + 125
    assert bank.pay_out(25) == 25
    assert bank.get_balance() == BANK_STARTING_FUNDS + 100


def test_pay_out_rejects_insufficient_funds():
    """Paying more than the bank holds should fail loudly."""
    bank = Bank()

    with pytest.raises(ValueError):
        bank.pay_out(BANK_STARTING_FUNDS + 1)


def test_give_loan_credits_player_and_reduces_bank_reserves():
    """Loans should move money from the bank to the player and be recorded."""
    bank = Bank()
    player = Player("Alice")

    bank.give_loan(player, 200)

    assert player.balance == STARTING_BALANCE + 200
    assert bank.get_balance() == BANK_STARTING_FUNDS - 200
    assert bank.total_loans_issued() == 200
    assert bank.loan_count() == 1
