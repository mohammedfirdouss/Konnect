"""
Test module for Konnect application
"""

from konnect.main import add_numbers, validate_payment_amount


def test_add_numbers():
    """Test the add_numbers function"""
    assert add_numbers(2, 3) == 5
    assert add_numbers(-1, 1) == 0
    assert add_numbers(0, 0) == 0


def test_validate_payment_amount():
    """Test payment amount validation"""
    # Valid amounts
    assert validate_payment_amount(10.5) is True
    assert validate_payment_amount(100) is True
    assert validate_payment_amount(999999) is True

    # Invalid amounts
    assert validate_payment_amount(0) is False
    assert validate_payment_amount(-10) is False
    assert validate_payment_amount(1000001) is False


def test_validate_payment_amount_edge_cases():
    """Test edge cases for payment validation"""
    assert validate_payment_amount(0.01) is True
    assert validate_payment_amount(1000000) is True
    assert validate_payment_amount(1000000.01) is False
