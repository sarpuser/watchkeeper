import pytest

from watchkeeper.monitoring.status_checkers.ping_checker import (
	PingStatus,
	ping,
	ping_command,
)

# Import constants for testing
from .values import (
	DUMMY_IP,
	EXECUTION_ERROR_HOST,
	LOCALHOST_HOST,
	LOCALHOST_IP,
	MALFORMED_OUTPUT_HOST,
	PARTIAL_LOSS_HOST,
	RTT_AVG,
	RTT_MAX,
	RTT_MIN,
	RTT_STD_DEV,
	TEST_NET_IPS,
	UNKNOWN_HOST,
)


# Tests for successful pings
@pytest.mark.parametrize(
	"address, icmp_count",
	[
		(LOCALHOST_HOST, ping_command.DEFAULT_ICMP_COUNT),
		(LOCALHOST_IP, ping_command.DEFAULT_ICMP_COUNT),
		(LOCALHOST_IP, 5),
		(LOCALHOST_IP, 10),
	],
)
def test_ping_parser_success(mock_ping_command, address, icmp_count):
	"""Test successful ping with various packet counts"""
	result = ping(address, icmp_count=icmp_count)

	assert result.hostname == address, f"{result.hostname=} == {address}"
	assert result.ip_address == LOCALHOST_IP, f"{result.ip_address=} == {LOCALHOST_IP}"
	assert result.packets_sent == icmp_count, f"{result.packets_sent=} == {icmp_count}"
	assert result.packets_received == icmp_count, (
		f"{result.packets_received=} == {icmp_count}"
	)
	assert result.packet_loss == 0, f"{result.packet_loss=} == 0"
	assert result.rtt_min == RTT_MIN, f"{result.rtt_min=} == {RTT_MIN}"
	assert result.rtt_avg == RTT_AVG, f"{result.rtt_avg=} == {RTT_AVG}"
	assert result.rtt_max == RTT_MAX, f"{result.rtt_max=} == {RTT_MAX}"
	assert result.rtt_std_dev == RTT_STD_DEV, f"{result.rtt_std_dev=} == {RTT_STD_DEV}"
	assert result.status == PingStatus.SUCCESS, (
		f"{result.status=} == {PingStatus.SUCCESS=}"
	)


# Tests for timeout pings
@pytest.mark.parametrize(
	"test_address, icmp_count",
	[
		(TEST_NET_IPS[0], ping_command.DEFAULT_ICMP_COUNT),
		(TEST_NET_IPS[1], ping_command.DEFAULT_ICMP_COUNT),
		(TEST_NET_IPS[2], ping_command.DEFAULT_ICMP_COUNT),
		(TEST_NET_IPS[0], 5),
		(TEST_NET_IPS[0], 10),
	],
)
def test_ping_parser_timeout(mock_ping_command, test_address, icmp_count):
	"""Test ping timeout with various packet counts"""
	result = ping(test_address, icmp_count=icmp_count)

	assert result.status == PingStatus.TIMEOUT, (
		f"{result.status=} == {PingStatus.TIMEOUT=}"
	)
	assert result.hostname == test_address, f"{result.hostname=} == {test_address}"
	assert result.ip_address == test_address, f"{result.ip_address=} == {test_address}"
	assert result.packets_sent == icmp_count, f"{result.packets_sent=} == {icmp_count}"
	assert result.packets_received == 0, f"{result.packets_received=} == 0"
	assert result.packet_loss == 100, f"{result.packet_loss=} == 100"
	assert result.rtt_min == 0, f"{result.rtt_min=} == 0"
	assert result.rtt_avg == 0, f"{result.rtt_avg=} == 0"
	assert result.rtt_max == 0, f"{result.rtt_max=} == 0"
	assert result.rtt_std_dev == 0, f"{result.rtt_std_dev=} == 0"


# Test for unknown host
def test_ping_parser_unknown_host(mock_ping_command):
	"""Test ping to unknown host"""
	result = ping(UNKNOWN_HOST)

	assert result.status == PingStatus.UNKNOWN_HOST, (
		f"{result.status=} == {PingStatus.UNKNOWN_HOST=}"
	)
	assert result.hostname == UNKNOWN_HOST, f"{result.hostname=} == {UNKNOWN_HOST}"
	assert result.ip_address is None, f"{result.ip_address=} == None"
	assert result.packets_sent == 0, f"{result.packets_sent=} == 0"
	assert result.packets_received == 0, f"{result.packets_received=} == 0"
	assert result.packet_loss == 0, f"{result.packet_loss=} == 0"
	assert result.rtt_min == 0, f"{result.rtt_min=} == 0"
	assert result.rtt_avg == 0, f"{result.rtt_avg=} == 0"
	assert result.rtt_max == 0, f"{result.rtt_max=} == 0"
	assert result.rtt_std_dev == 0, f"{result.rtt_std_dev=} == 0"


# Test for partial packet loss
@pytest.mark.parametrize("icmp_count", [5, 10])
def test_ping_parser_success_partial_loss(mock_ping_command, icmp_count):
	"""Test ping with partial packet loss"""
	result = ping(PARTIAL_LOSS_HOST, icmp_count=icmp_count)

	received_packets = max(1, icmp_count // 2)  # At least 1, about half lost
	lost_packets = icmp_count - received_packets
	loss_percent = (lost_packets / icmp_count) * 100

	assert result.hostname == PARTIAL_LOSS_HOST, (
		f"{result.hostname=} == {PARTIAL_LOSS_HOST=}"
	)
	assert result.ip_address == DUMMY_IP, f"{result.ip_address=} == {DUMMY_IP}"
	assert result.packets_sent == icmp_count, f"{result.packets_sent=} == {icmp_count}"
	assert result.packets_received == received_packets, (
		f"{result.packets_received=} == {received_packets}"
	)
	assert result.packet_loss == loss_percent, (
		f"{result.packet_loss=} == {loss_percent}"
	)
	assert result.rtt_min == RTT_MIN, f"{result.rtt_min=} == {RTT_MIN}"
	assert result.rtt_avg == RTT_AVG, f"{result.rtt_avg=} == {RTT_AVG}"
	assert result.rtt_max == RTT_MAX, f"{result.rtt_max=} == {RTT_MAX}"
	assert result.rtt_std_dev == RTT_STD_DEV, f"{result.rtt_std_dev=} == {RTT_STD_DEV}"
	assert result.status == PingStatus.SUCCESS, (
		f"{result.status=} == {PingStatus.SUCCESS=}"
	)


# Malformed output test
def test_ping_parser_malformed_output(mock_ping_command):
	"""Test handling of malformed ping output"""
	result = ping(MALFORMED_OUTPUT_HOST)

	assert result.status == PingStatus.PARSE_ERROR, (
		f"{result.status=} == {PingStatus.PARSE_ERROR}"
	)
	assert result.hostname == MALFORMED_OUTPUT_HOST, (
		f"{result.hostname=} == {MALFORMED_OUTPUT_HOST}"
	)
	assert result.ip_address is None, f"{result.ip_address=} == None"
	assert result.packets_sent == 0, f"{result.packets_sent=} == 0"
	assert result.packets_received == 0, f"{result.packets_received=} == 0"
	assert result.packet_loss == 0, f"{result.packet_loss=} == 0"
	assert result.rtt_min == 0, f"{result.rtt_min=} == 0"
	assert result.rtt_avg == 0, f"{result.rtt_avg=} == 0"
	assert result.rtt_max == 0, f"{result.rtt_max=} == 0"
	assert result.rtt_std_dev == 0, f"{result.rtt_std_dev=} == 0"


# Command execution error test
def test_ping_command_execution_error(mock_ping_command):
	"""Test handling of command execution errors"""

	result = ping(EXECUTION_ERROR_HOST)

	assert result.status == PingStatus.EXECUTION_ERROR, (
		f"{result.status=} == {PingStatus.EXECUTION_ERROR}"
	)
	assert result.hostname == EXECUTION_ERROR_HOST, (
		f"{result.hostname=} == {EXECUTION_ERROR_HOST}"
	)
	assert result.ip_address is None, f"{result.ip_address=} == None"
	assert result.packets_sent == 0, f"{result.packets_sent=} == 0"
	assert result.packets_received == 0, f"{result.packets_received=} == 0"
	assert result.packet_loss == 0, f"{result.packet_loss=} == 0"
	assert result.rtt_min == 0, f"{result.rtt_min=} == 0"
	assert result.rtt_avg == 0, f"{result.rtt_avg=} == 0"
	assert result.rtt_max == 0, f"{result.rtt_max=} == 0"
	assert result.rtt_std_dev == 0, f"{result.rtt_std_dev=} == 0"


# Network unreachable error test
@pytest.mark.parametrize("icmp_count", [ping_command.DEFAULT_ICMP_COUNT, 5])
def test_ping_parser_network_unreachable(mock_ping_command, icmp_count):
	"""Test parsing ping output when network is unreachable"""
	result = ping(DUMMY_IP, icmp_count=icmp_count)

	assert result.ip_address == DUMMY_IP, f"{result.ip_address=} == {DUMMY_IP}"
	assert result.status == PingStatus.NETWORK_ERROR, (
		f"{result.status=} == {PingStatus.NETWORK_ERROR}"
	)
	assert result.packets_sent == icmp_count, f"{result.packets_sent=} == {icmp_count}"
	assert result.packets_received == 0, f"{result.packets_received=} == 0"
	assert result.packet_loss == 100, f"{result.packet_loss=} == 100"
	assert result.rtt_min == 0, f"{result.rtt_min=} == 0"
	assert result.rtt_avg == 0, f"{result.rtt_avg=} == 0"
	assert result.rtt_max == 0, f"{result.rtt_max=} == 0"
	assert result.rtt_std_dev == 0, f"{result.rtt_std_dev=} == 0"
