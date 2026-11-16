from decimal import Decimal

from framework.models.bet import Bet
from framework.bet_repository import BetRepository


def test_save_and_retrieve_open_bet():
    repository = BetRepository()

    bet = Bet(
        bet_id="BET-001",
        selection_id="SEL-001",
        stake=Decimal("20.00"),
        odds=Decimal("2.50"),
        status="OPEN",
        customer_id="CUST-001",
    )

    repository.save(bet)

    stored_bet = repository.get_bet("BET-001")
    open_bets = repository.get_open_bets("CUST-001")

    assert stored_bet is not None
    assert stored_bet.bet_id == bet.bet_id
    assert stored_bet.status == "OPEN"

    assert len(open_bets) == 1
    assert open_bets[0].bet_id == bet.bet_id
    assert open_bets[0].stake == bet.stake
    assert open_bets[0].odds == bet.odds

def test_open_bets_are_customer_specific():
    repository = BetRepository()

    bet_customer_a = Bet(
        bet_id="BET-001",
        customer_id="CUST-001",
        selection_id="SEL-001",
        stake=Decimal("20.00"),
        odds=Decimal("2.50"),
        status="OPEN"
    )

    bet_customer_b = Bet(
        bet_id="BET-002",
        customer_id="CUST-002",
        selection_id="SEL-002",
        stake=Decimal("30.00"),
        odds=Decimal("3.00"),
        status="OPEN"
    )

    repository.save(bet_customer_a)
    repository.save(bet_customer_b)

    open_bets_a = repository.get_open_bets("CUST-001")
    open_bets_b = repository.get_open_bets("CUST-002")

    assert len(open_bets_a) == 1
    assert open_bets_a[0].bet_id == "BET-001"
    assert open_bets_a[0].customer_id == "CUST-001"

    assert len(open_bets_b) == 1
    assert open_bets_b[0].bet_id == "BET-002"
    assert open_bets_b[0].customer_id == "CUST-002"