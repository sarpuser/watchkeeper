# tests/unit/monitoring/status_checkers/ping/test_ping.py

import platform

import pytest

from watchkeeper.monitoring.status_checkers.ping.ping import PingStatus, ping

# Import constants for testing
from .values import (
    LOCALHOST_HOST,
    LOCALHOST_IP,
    PARTIAL_LOSS_HOST,
    PARTIAL_LOSS_IP,
    RTT_AVG,
    RTT_MAX,
    RTT_MIN,
    RTT_STD_DEV,
    TEST_NET_IPS,
    UNKNOWN_HOST,
)


# Tests for successful pings
@pytest.mark.parametrize("localhost_address", [LOCALHOST_HOST, LOCALHOST_IP])
def test_ping_parser_success_no_packet_loss(mock_ping_command, localhost_address):
    """Test successful ping with no packet loss"""
    result = ping(localhost_address)

    assert result.hostname == localhost_address
    assert result.ip_address == LOCALHOST_IP
    assert result.packets_sent == 1
    assert result.packets_received == 1
    assert result.packet_loss == 0
    assert result.rtt_min == RTT_MIN
    assert result.rtt_avg == RTT_AVG
    assert result.rtt_max == RTT_MAX

    if platform.system() != "Windows":
        assert result.rtt_std_dev == RTT_STD_DEV

    assert result.error == PingStatus.SUCCESS

@pytest.mark.parametrize("icmp_count", [5, 10])
def test_ping_parser_success_multiple_packets(mock_ping_command, icmp_count):
    """Test successful ping with multiple packets"""
    result = ping(LOCALHOST_IP, icmp_count=icmp_count)

    assert result.hostname == LOCALHOST_IP
    assert result.ip_address == LOCALHOST_IP
    assert result.packets_sent == icmp_count
    assert result.packets_received == icmp_count
    assert result.packet_loss == 0
    assert result.rtt_min == RTT_MIN
    assert result.rtt_avg == RTT_AVG
    assert result.rtt_max == RTT_MAX
    assert result.error == PingStatus.SUCCESS

# Tests for timeout pings
@pytest.mark.parametrize("test_net_address", TEST_NET_IPS)
def test_ping_parser_timeout(mock_ping_command, test_net_address):
    """Test ping timeout (no responses)"""
    result = ping(test_net_address)

    assert result.hostname == test_net_address
    assert result.ip_address == test_net_address  # For TEST_NET_IPs, IP is same as hostname
    assert result.packets_sent == 1
    assert result.packets_received == 0
    assert result.packet_loss == 100
    assert result.rtt_min == 0
    assert result.rtt_avg == 0
    assert result.rtt_max == 0

    if platform.system() != "Windows":
        assert result.rtt_std_dev == 0

    assert result.error == PingStatus.TIMEOUT

@pytest.mark.parametrize("icmp_count", [5, 10])
def test_ping_parser_timeout_multiple_packets(mock_ping_command, icmp_count):
    """Test ping timeout with multiple packets"""
    test_net_address = TEST_NET_IPS[0]
    result = ping(test_net_address, icmp_count=icmp_count)

    assert result.hostname == test_net_address
    assert result.ip_address == test_net_address
    assert result.packets_sent == icmp_count
    assert result.packets_received == 0
    assert result.packet_loss == 100
    assert result.rtt_min == 0
    assert result.rtt_avg == 0
    assert result.rtt_max == 0
    assert result.error == PingStatus.TIMEOUT

# Tests for unknown host
def test_ping_parser_unknown_host(mock_ping_command):
    """Test ping to unknown host"""
    result = ping(UNKNOWN_HOST)

    assert result.hostname == UNKNOWN_HOST
    assert result.ip_address is None
    assert result.packets_sent == 0
    assert result.packets_received == 0
    assert result.packet_loss == 0
    assert result.rtt_min == 0
    assert result.rtt_avg == 0
    assert result.rtt_max == 0

    if platform.system() != "Windows":
        assert result.rtt_std_dev is None

    assert result.error == PingStatus.UNKNOWN_HOST

# Tests for partial packet loss
@pytest.mark.parametrize("icmp_count", [5, 10])
def test_ping_parser_success_partial_loss(mock_ping_command, icmp_count):
    """Test ping with partial packet loss"""
    result = ping(PARTIAL_LOSS_HOST, icmp_count=icmp_count)

    received_packets = max(1, icmp_count // 2)  # At least 1, about half lost
    lost_packets = icmp_count - received_packets
    loss_percent = (lost_packets / icmp_count) * 100

    assert result.hostname == PARTIAL_LOSS_HOST
    assert result.ip_address == PARTIAL_LOSS_IP  # The mock IP we assigned
    assert result.packets_sent == icmp_count
    assert result.packets_received == received_packets
    assert result.packet_loss == loss_percent
    assert result.rtt_min == RTT_MIN
    assert result.rtt_avg == RTT_AVG
    assert result.rtt_max == RTT_STD_DEV

    if platform.system() != "Windows":
        assert result.rtt_std_dev is not None

    # Partial loss should still be considered successful if some packets got through
    assert result.error == PingStatus.SUCCESS

# Edge case tests
def test_ping_parser_with_custom_timeout(mock_ping_command):
    """Test ping with custom timeout value"""
    custom_timeout = 5
    result = ping(LOCALHOST_IP, timeout=custom_timeout)

    # The mock doesn't actually use the timeout, but we want to ensure
    # the function accepts and passes this parameter correctly
    assert result.hostname == LOCALHOST_IP
    assert result.error == PingStatus.SUCCESS

def test_ping_parser_default_parameters(mock_ping_command):
    """Test ping with default parameters"""
    result = ping(LOCALHOST_IP)

    assert result.hostname == LOCALHOST_IP
    assert result.packets_sent == 1  # Default is 1 packet
    assert result.error == PingStatus.SUCCESS

def test_ip_resolution_behavior(mock_ping_command):
    """Test how ping handles hostname vs IP address input"""
    host_result = ping(LOCALHOST_HOST)
    ip_result = ping(LOCALHOST_IP)

    # Both should resolve to the same IP
    assert host_result.ip_address == ip_result.ip_address == LOCALHOST_IP

@pytest.mark.parametrize("icmp_count", [-1, 0])
def test_ping_parser_invalid_icmp_count(monkeypatch, icmp_count):
    # Should throw a ValueError if icmp_count < 1
    with pytest.raises(ValueError):
        ping(LOCALHOST_HOST, icmp_count = icmp_count)

@pytest.mark.parametrize("timeout", [-1, 0])
def test_ping_parser_invalid_timeout(monkeypatch, timeout):
    # Should throw a ValueError if icmp_count < 1
    with pytest.raises(ValueError):
        ping(LOCALHOST_HOST, timeout = timeout)

def test_ping_parser_malformed_output(monkeypatch):
    """Test handling of malformed ping output"""
    def mock_bad_output(*args, **kwargs):
        class BadProcess:
            def __init__(self):
                self.returncode = 0
                self.stdout = "This is not a valid ping output format"
                self.stderr = ""
        return BadProcess()

    from watchkeeper.monitoring.status_checkers.ping import ping
    monkeypatch.setattr(ping, "_execute_ping_command", mock_bad_output)

    # Should handle gracefully without exceptions
    result = ping.ping(LOCALHOST_HOST)

    # Test that we get reasonable defaults for an unparseable response
    assert result.hostname == "localhost"
    assert result.ip_address is None
    assert result.packets_sent == 0  # Can't determine from bad output
    assert result.packets_received == 0  # Can't determine from bad output
    assert result.packet_loss == 0   # Can't determine from bad output
    assert result.rtt_min == 0
    assert result.rtt_avg == 0
    assert result.rtt_max == 0
    assert result.rtt_std_dev == 0
    assert result.error == PingStatus.PARSE_ERROR

def test_ping_command_execution_error(monkeypatch):
    """Test handling of command execution errors"""
    import subprocess

    def mock_failing_command(*args, **kwargs):
        raise subprocess.SubprocessError("Command failed to execute")

    from watchkeeper.monitoring.status_checkers.ping import ping
    monkeypatch.setattr(ping, "_execute_ping_command", mock_failing_command)

    result = ping.ping(LOCALHOST_HOST)

    # Verify the result contains appropriate error information
    assert result.hostname == "localhost"
    assert result.ip_address is None
    assert result.packets_sent == 0
    assert result.packets_received == 0
    assert result.packet_loss == 0
    assert result.rtt_min == 0
    assert result.rtt_avg == 0
    assert result.rtt_max == 0
    assert result.rtt_std_dev == 0
    assert result.error == PingStatus.EXECUTION_ERROR