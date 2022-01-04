from main import get_book


def test_get_book():
    assert get_book() > 0
