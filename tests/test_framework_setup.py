import pytest
import requests
import selenium


@pytest.mark.smoke
def test_framework_dependencies():
    """Verify that the core automation dependencies are available."""

    assert requests.__version__
    assert selenium.__version__