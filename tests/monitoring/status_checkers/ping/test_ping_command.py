import pytest

from watchkeeper.monitoring.status_checkers.ping_checker import (
	PingStatus,
	ping,
)

from .values import LOCALHOST_HOST, LOCALHOST_IP, TEST_NET_IPS, UNKNOWN_HOST


@pytest.mark.parametrize("localhost_address", [LOCALHOST_HOST, LOCALHOST_IP])
@pytest.mark.flaky(retries=3)
def test_ping_command_localhost_success(localhost_address):
	result = ping(localhost_address)

	assert result.status == PingStatus.SUCCESS, (
		f"{result.status=} == {PingStatus.SUCCESS}"
	)
	assert result.hostname == localhost_address, (
		f"{result.hostname=} == {localhost_address}"
	)
	assert result.ip_address == LOCALHOST_IP, f"{result.ip_address=} == {LOCALHOST_IP}"
	assert result.packet_loss == 0, f"{result.packet_loss=} == 0"
	assert result.rtt_max < 0.5, f"{result.rtt_max=} < 0.5"


@pytest.mark.parametrize("icmp_count", [5, 10])
@pytest.mark.flaky(retries=3)
def test_ping_command_icmp_count(icmp_count):
	result = ping(LOCALHOST_HOST, icmp_count=icmp_count)

	assert result.packets_sent == icmp_count, f"{result.packets_sent=} == {icmp_count}"
	assert result.packets_received == icmp_count, (
		f"{result.packets_received=} == {icmp_count}"
	)
	assert result.packet_loss == 0, f"{result.packet_loss=} == {icmp_count}"


@pytest.mark.parametrize("public_dns_address", ["1.1.1.1", "8.8.8.8"])
@pytest.mark.flaky(retries=3)
def test_ping_command_public_dns_success(public_dns_address):
	result = ping(public_dns_address)

	assert result.status == PingStatus.SUCCESS, (
		f"{result.status=} == {PingStatus.SUCCESS}"
	)
	assert result.ip_address == public_dns_address, (
		f"{result.ip_address=} == {public_dns_address}"
	)


def test_ping_command_timeout():
	result = ping(TEST_NET_IPS[0])

	assert result.status == PingStatus.TIMEOUT, (
		f"{result.status=} == {PingStatus.TIMEOUT}"
	)


def test_ping_command_unknown_host():
	result = ping(UNKNOWN_HOST)

	assert result.status == PingStatus.UNKNOWN_HOST, (
		f"{result.status=} == {UNKNOWN_HOST}"
	)
	assert result.ip_address is None, f"{result.ip_address=} == None"


# Invalid parameter tests
@pytest.mark.parametrize("icmp_count,", [-1, 0])
def test_ping_parser_invalid_values(icmp_count):
	"""Test invalid ICMP count parameter"""
	result = ping(LOCALHOST_HOST, icmp_count=icmp_count)

	assert result.status == PingStatus.COMMAND_ERROR
	assert result.ip_address is None, f"{result.ip_address=} == None"


@pytest.mark.parametrize("timeout", [-1, 0])
def test_ping_parser_invalid_timeout(timeout):
	"""Test invalid timeout parameter"""
	result = ping(LOCALHOST_HOST, timeout=timeout)

	assert result.status == PingStatus.COMMAND_ERROR
	assert result.ip_address is None, f"{result.ip_address=} == None"
