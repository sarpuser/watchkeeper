from watchkeeper.utils.ip_address import IPAddress
import pytest


@pytest.mark.parametrize(
	"valid_ip_address", ["0.0.0.0", "255.255.255.255", "12.234.88.198"]
)
def test_ip_address_valid(valid_ip_address):
	try:
		IPAddress(valid_ip_address)
	except ValueError:
		pytest.fail(f"IP address {valid_ip_address} should be valid but is not")


@pytest.mark.parametrize("short_ip_address", ["123", "123.123", "123.123.123"])
def test_ip_address_short(short_ip_address):
	with pytest.raises(ValueError):
		IPAddress(short_ip_address)


def test_ip_address_short_with_trailing_period():
	with pytest.raises(ValueError):
		IPAddress("123.123.123.")


def test_ip_address_short_with_leading_period():
	with pytest.raises(ValueError):
		IPAddress(".123.123.123")


def test_ip_address_long():
	with pytest.raises(ValueError):
		IPAddress("123.123.123.123.123")


@pytest.mark.parametrize(
	"large_octet_ip_address",
	["256.123.123.123", "123.256.123.123", "123.123.256.123", "123.123.123.256"],
)
def test_ip_address_large_octet(large_octet_ip_address):
	with pytest.raises(ValueError):
		IPAddress(large_octet_ip_address)


def test_ip_address_leading_period():
	with pytest.raises(ValueError):
		IPAddress(".123.123.123.123")


def test_ip_address_trailing_period():
	with pytest.raises(ValueError):
		IPAddress("123.123.123.123.")


@pytest.mark.parametrize(
	"invalid_chars_ip_address",
	["a+3.123.123.123", "123.a+3.123.123", "123.123.a+3.123", "123.123.123.a+3"],
)
def test_ip_address_invalid_chars(invalid_chars_ip_address):
	with pytest.raises(ValueError):
		IPAddress(invalid_chars_ip_address)
