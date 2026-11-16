from decimal import Decimal
from framework.models.selection import Selection


def test_selection_is_available():
    selection = Selection(
        selection_id="SEL-001",
        odds=Decimal("2.50"),
        available=True
    )

    assert selection.selection_id == "SEL-001"
    assert selection.odds == Decimal("2.50")
    assert selection.available is True