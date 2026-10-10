
import pytest
from solution import cidr_contains

def test_inside_outside():
    assert cidr_contains("192.168.1.0/24", "192.168.1.77") is True
    assert cidr_contains("192.168.1.0/24", "192.168.2.1") is False
    assert cidr_contains("10.0.0.0/8", "10.255.255.255") is True
    assert cidr_contains("10.0.0.0/8", "11.0.0.0") is False

def test_edges():
    assert cidr_contains("0.0.0.0/0", "8.8.8.8") is True
    assert cidr_contains("1.2.3.4/32", "1.2.3.4") is True
    assert cidr_contains("1.2.3.4/32", "1.2.3.5") is False
    assert cidr_contains("10.0.0.5/8", "10.9.9.9") is True

@pytest.mark.parametrize("cidr,ip", [("1.2.3.4/33", "1.2.3.4"), ("abc", "1.1.1.1"), ("10.0.0.0/8", "300.1.1.1"),
                                      ("10.0.0.0/8", "::1"), ("10.0.0/8", "10.0.0.1"), ("10.0.0.0/-1", "10.0.0.1"), ("::1/128", "::1")])
def test_invalid(cidr, ip):
    with pytest.raises(ValueError):
        cidr_contains(cidr, ip)
