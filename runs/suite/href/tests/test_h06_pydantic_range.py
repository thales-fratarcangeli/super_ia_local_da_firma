import pytest
from datetime import date
from pydantic import ValidationError
from solution import Booking

def test_ok_and_nights_computed():
    b = Booking(guest="Ana", start="2026-03-01", end="2026-03-05")
    assert b.nights == 4 and b.start == date(2026, 3, 1)

def test_nights_overridden():
    assert Booking(guest="Ana", start="2026-03-01", end="2026-03-02", nights=99).nights == 1

def test_end_must_be_after_start():
    for end in ["2026-03-01", "2026-02-28"]:
        with pytest.raises(ValidationError):
            Booking(guest="Ana", start="2026-03-01", end=end)

def test_guest_required():
    with pytest.raises(ValidationError):
        Booking(guest="", start="2026-03-01", end="2026-03-02")
