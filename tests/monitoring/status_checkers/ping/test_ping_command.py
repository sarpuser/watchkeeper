import pytest

from watchkeeper.monitoring.status_checkers.ping.ping import PingStatus, ping

from .values import LOCALHOST_HOST, LOCALHOST_IP, TEST_NET_IPS, UNKNOWN_HOST


@pytest.mark.parametrize("localhost_address", [LOCALHOST_HOST, LOCALHOST_IP])
def test_ping_command_localhost_success(localhost_address):
	result = ping(localhost_address)

	assert result.error == PingStatus.SUCCESS, (
		f"{result.error=} == {PingStatus.SUCCESS}"
	)
	assert result.hostname == localhost_address, (
		f"{result.hostname=} == {localhost_address}"
	)
	assert result.ip_address == LOCALHOST_IP, f"{result.ip_address=} == {LOCALHOST_IP}"
	assert result.packet_loss == 0, f"{result.packet_loss=} == 0"
	assert result.rtt_max < 0.2, f"{result.rtt_max=}, 0.2"


@pytest.mark.parametrize("icmp_count", [5, 10])
def test_ping_command_icmp_count(icmp_count):
	result = ping(LOCALHOST_HOST)

	assert result.packets_sent == icmp_count, f"{result.packets_sent=} == {icmp_count}"
	assert result.packets_received == icmp_count, (
		f"{result.packets_received=} == {icmp_count}"
	)
	assert result.packet_loss == 0, f"{result.packet_loss=} == {icmp_count}"


@pytest.mark.parametrize("public_dns_address", ["1.1.1.1", "8.8.8.8"])
def test_ping_command_public_dns_success(public_dns_address):
	result = ping(public_dns_address)

	assert result.error == PingStatus.SUCCESS, (
		f"{result.error=} == {PingStatus.SUCCESS}"
	)
	assert result.ip_address == public_dns_address, (
		f"{result.ip_address=} == {public_dns_address}"
	)


def test_ping_command_timeout():
	result = ping(TEST_NET_IPS[0])

	assert result.error == PingStatus.TIMEOUT, (
		f"{result.error=} == {PingStatus.TIMEOUT}"
	)


def test_ping_command_unknown_host():
	result = ping(UNKNOWN_HOST)

	assert result.error == PingStatus.UNKNOWN_HOST, f"{result.error=} == {UNKNOWN_HOST}"
