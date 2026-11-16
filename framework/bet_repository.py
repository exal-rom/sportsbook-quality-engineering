from framework.models.bet import Bet


class BetRepository:

    def __init__(self):
        self._bets = {}

    def save(self, bet: Bet) -> None:
        self._bets[bet.bet_id] = bet

    def get_bet(self, bet_id: str) -> Bet | None:
        return self._bets.get(bet_id)

    def get_open_bets(self, customer_id: str) -> list[Bet]:
        return [
            bet
            for bet in self._bets.values()
            if bet.customer_id == customer_id
            and bet.status == "OPEN"
        ]