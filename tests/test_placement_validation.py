import pytest
from decimal import Decimal
from framework.models.selection import Selection
from framework.placement import validate_selection
from framework.models.account import Account
from framework.placement import validate_financial_conditions
from framework.placement import can_place_bet
from framework.placement import place_bet
from framework.bet_repository import BetRepository


def test_available_selection():
    selection = Selection(
        selection_id="SEL-001",
        odds=Decimal("2.50"),
        available=True
    )

    assert validate_selection(selection) is True


def test_unavailable_selection():
    selection = Selection(
        selection_id="SEL-002",
        odds=Decimal("2.50"),
        available=False
    )

    assert validate_selection(selection) is False

def test_valid_financial_conditions():
    account = Account(
        account_id="ACC-001",
        available_balance=Decimal("100.00"),
        max_stake=Decimal("50.00"),
        max_liability=Decimal("200.00")
    )

    stake = Decimal("20.00")
    odds = Decimal("3.00")

    assert validate_financial_conditions(
        account, stake, odds
    ) is True

def test_insufficient_balance():
    account = Account(
        account_id="ACC-001",
        available_balance=Decimal("10.00"),
        max_stake=Decimal("50.00"),
        max_liability=Decimal("200.00")
    )

    stake = Decimal("20.00")
    odds = Decimal("3.00")

    assert validate_financial_conditions(
        account, stake, odds
    ) is False

def test_stake_exceeds_maximum():
    account = Account(
        account_id="ACC-001",
        available_balance=Decimal("100.00"),
        max_stake=Decimal("50.00"),
        max_liability=Decimal("200.00")
    )

    stake = Decimal("60.00")
    odds = Decimal("3.00")

    assert validate_financial_conditions(
        account, stake, odds
    ) is False

def test_liability_limit_exceeded():
    account = Account(
        account_id="ACC-001",
        available_balance=Decimal("100.00"),
        max_stake=Decimal("50.00"),
        max_liability=Decimal("200.00")
    )

    stake = Decimal("20.00")
    odds = Decimal("15.00")

    assert validate_financial_conditions(
        account, stake, odds
    ) is False

@pytest.mark.parametrize(
    "stake",
    [
        Decimal("0.00"),
        Decimal("-10.00")
    ]
)
def test_invalid_stake_amount(stake):
    account = Account(
        account_id="ACC-001",
        available_balance=Decimal("100.00"),
        max_stake=Decimal("50.00"),
        max_liability=Decimal("200.00")
    )

    assert validate_financial_conditions(
        account,
        stake,
        Decimal("3.00")
    ) is False

@pytest.mark.parametrize(
    "stake",
    [
        Decimal("0.00"),
        Decimal("-10.00")
    ]
)
def test_invalid_stake_amount(stake):
    account = Account(
        account_id="ACC-001",
        available_balance=Decimal("100.00"),
        max_stake=Decimal("50.00"),
        max_liability=Decimal("200.00")
    )

    assert validate_financial_conditions(
        account,
        stake,
        Decimal("3.00")
    ) is False

def test_valid_bet_is_eligible_for_placement():
    selection = Selection(
        selection_id="SEL-001",
        odds=Decimal("2.50"),
        available=True
    )

    account = Account(
        account_id="ACC-001",
        available_balance=Decimal("100.00"),
        max_stake=Decimal("50.00"),
        max_liability=Decimal("200.00")
    )

    stake = Decimal("20.00")

    assert can_place_bet(
        selection,
        account,
        stake
    ) is True

def test_unavailable_selection_prevents_placement():
    selection = Selection(
        selection_id="SEL-001",
        odds=Decimal("2.50"),
        available=False
    )

    account = Account(
        account_id="ACC-001",
        available_balance=Decimal("100.00"),
        max_stake=Decimal("50.00"),
        max_liability=Decimal("200.00")
    )

    stake = Decimal("20.00")

    assert can_place_bet(
        selection,
        account,
        stake
    ) is False

def test_successful_bet_creation():
    selection = Selection(
        selection_id="SEL-001",
        odds=Decimal("2.50"),
        available=True
    )

    account = Account(
        account_id="ACC-001",
        available_balance=Decimal("100.00"),
        max_stake=Decimal("50.00"),
        max_liability=Decimal("200.00")
    )

    stake = Decimal("20.00")
    repository = BetRepository()

    # Place the bet
    bet = bet = place_bet(
        selection,
        account,
        stake,
        repository,
        customer_id="CUST-001"
    )

    # Verify placement
    assert bet is not None
    assert bet.bet_id
    assert bet.status == "OPEN"
    assert bet.customer_id == "CUST-001"

    # Verify the accepted stake was debited
    assert account.available_balance == Decimal("80.00")
    assert bet.stake == Decimal("20.00")

    # Retrieve the bet independently from the repository
    open_bets = repository.get_open_bets("CUST-001")
    # Find the placed bet by its Bet ID
    matching_bets = [
        open_bet
        for open_bet in open_bets
        if open_bet.bet_id == bet.bet_id
    ]

    # Verify the bet exists exactly once in Open Bets
    assert len(matching_bets) == 1

    stored_bet = matching_bets[0]
    assert stored_bet.customer_id == "CUST-001"

    # Verify the recorded bet details
    assert stored_bet.status == "OPEN"
    assert stored_bet.selection_id == selection.selection_id
    assert stored_bet.stake == stake
    assert stored_bet.odds == selection.odds

    # Verify the bet does not appear in another customer's Open Bets
    other_customer_open_bets = repository.get_open_bets("CUST-002")

    assert not any(
        open_bet.bet_id == bet.bet_id
        for open_bet in other_customer_open_bets
    )

def test_each_placed_bet_has_unique_id():
    repository = BetRepository()

    selection = Selection(
        selection_id="SEL-001",
        odds=Decimal("2.50"),
        available=True
    )

    account = Account(
        account_id="ACC-001",
        available_balance=Decimal("100.00"),
        max_stake=Decimal("50.00"),
        max_liability=Decimal("200.00")
    )

    first_bet = place_bet(
        selection, account, Decimal("20.00"),
        repository, customer_id="CUST-001"
    )

    second_bet = place_bet(
        selection, account, Decimal("20.00"),
        repository, customer_id="CUST-001"
    )

    assert first_bet is not None
    assert second_bet is not None

    assert first_bet.bet_id != second_bet.bet_id

    open_bets = repository.get_open_bets("CUST-001")

    assert len(open_bets) == 2
    assert {bet.bet_id for bet in open_bets} == {
        first_bet.bet_id,
        second_bet.bet_id
    }

def test_second_bet_rejected_after_balance_debit():
    repository = BetRepository()

    selection = Selection(
        selection_id="SEL-001",
        odds=Decimal("2.00"),
        available=True
    )

    account = Account(
        account_id="ACC-001",
        available_balance=Decimal("100.00"),
        max_stake=Decimal("100.00"),
        max_liability=Decimal("200.00")
    )

    first_bet = place_bet(
        selection,
        account,
        Decimal("60.00"),
        repository,
        customer_id="CUST-001"
    )

    assert first_bet is not None
    assert first_bet.status == "OPEN"
    assert account.available_balance == Decimal("40.00")

    second_bet = place_bet(
        selection,
        account,
        Decimal("60.00"),
        repository,
        customer_id="CUST-001"
    )

    assert second_bet is None

    # Rejected placement must not debit the balance
    assert account.available_balance == Decimal("40.00")

    # Only the accepted bet must appear in Open Bets
    open_bets = repository.get_open_bets("CUST-001")

    assert len(open_bets) == 1
    assert open_bets[0].bet_id == first_bet.bet_id

def test_rejected_bet_does_not_debit_balance():
    repository = BetRepository()

    selection = Selection(
        selection_id="SEL-001",
        odds=Decimal("2.50"),
        available=False
    )

    account = Account(
        account_id="ACC-001",
        available_balance=Decimal("100.00"),
        max_stake=Decimal("50.00"),
        max_liability=Decimal("200.00")
    )

    initial_balance = account.available_balance

    bet = place_bet(
        selection,
        account,
        Decimal("20.00"),
        repository,
        customer_id="CUST-001"
    )

    # Placement must be rejected
    assert bet is None

    # No money must be debited
    assert account.available_balance == initial_balance

    # No bet must appear in Open Bets
    assert repository.get_open_bets("CUST-001") == []

@pytest.mark.parametrize(
    "stake, balance, max_stake, max_liability",
    [
        (Decimal("0"), Decimal("100"), Decimal("50"), Decimal("200")),
        (Decimal("-10"), Decimal("100"), Decimal("50"), Decimal("200")),
        (Decimal("120"), Decimal("100"), Decimal("150"), Decimal("200")),
        (Decimal("60"), Decimal("100"), Decimal("50"), Decimal("200")),
        (Decimal("50"), Decimal("100"), Decimal("100"), Decimal("50")),
    ]
)
def test_financial_rejection_does_not_modify_account(
    stake, balance, max_stake, max_liability
):
    repository = BetRepository()

    selection = Selection(
        selection_id="SEL-001",
        odds=Decimal("2.50"),
        available=True
    )

    account = Account(
        account_id="ACC-001",
        available_balance=balance,
        max_stake=max_stake,
        max_liability=max_liability
    )

    initial_balance = account.available_balance

    bet = place_bet(
        selection,
        account,
        stake,
        repository,
        customer_id="CUST-001"
    )

    assert bet is None
    assert account.available_balance == initial_balance
    assert repository.get_open_bets("CUST-001") == []

@pytest.mark.parametrize(
    "stake, balance, max_stake, max_liability",
    [
        (Decimal("100"), Decimal("100"), Decimal("150"), Decimal("200")),
        (Decimal("50"), Decimal("100"), Decimal("50"), Decimal("200")),
        (Decimal("50"), Decimal("100"), Decimal("100"), Decimal("75")),
    ]
)
def test_bet_accepted_at_financial_boundaries(
    stake, balance, max_stake, max_liability
):
    repository = BetRepository()

    selection = Selection(
        selection_id="SEL-001",
        odds=Decimal("2.50"),
        available=True
    )

    account = Account(
        account_id="ACC-001",
        available_balance=balance,
        max_stake=max_stake,
        max_liability=max_liability
    )

    initial_balance = account.available_balance

    bet = place_bet(
        selection,
        account,
        stake,
        repository,
        customer_id="CUST-001"
    )

    assert bet is not None
    assert bet.status == "OPEN"
    assert bet.stake == stake

    # Stake must be debited exactly once
    assert account.available_balance == initial_balance - stake

    # Accepted bet must be visible to the correct customer
    open_bets = repository.get_open_bets("CUST-001")

    assert len(open_bets) == 1
    assert open_bets[0].bet_id == bet.bet_id