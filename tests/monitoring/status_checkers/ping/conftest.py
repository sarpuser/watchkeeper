import platform

import pytest

from watchkeeper.monitoring.status_checkers.ping import ping

from .values import (
    LOCALHOST_HOST,
    LOCALHOST_IP,
    PARTIAL_LOSS_HOST,
    PARTIAL_LOSS_IP,
    PING_OUTPUT_FORMATS,
    RTT_AVG,
    TEST_NET_IPS,
    UNKNOWN_HOST,
)


@pytest.fixture
def mock_ping_command(monkeypatch):
    """Fixture to simulate ping command output for different scenarios"""

    class MockCompletedProcess:
        def __init__(self, returncode, stdout):
            self.returncode = returncode
            self.stdout = stdout
            self.stderr = ""

    def _generate_ping_responses(ip_address, icmp_count, response_template):
        """Generate individual ping response lines"""
        responses = ""
        for seq in range(1, icmp_count + 1):
            # Vary the RTT slightly for each packet
            rtt_time = RTT_AVG + ((seq - 1) * 0.005)
            responses += response_template.format(
                ip_address=ip_address, seq=seq, rtt_time=rtt_time
            )
        return responses

    def _mock_successful_ping(address, icmp_count, output_formats):
        """Generate a successful ping response"""
        ip_address = LOCALHOST_IP
        ping_responses = _generate_ping_responses(
            ip_address, icmp_count, output_formats["success_response_line"]
        )
        stdout = output_formats["success_format"].format(
            icmp_count=icmp_count,
            address=address,
            ip_address=ip_address,
            ping_responses=ping_responses
        )
        return MockCompletedProcess(0, stdout)

    def _mock_unknown_host(address, output_formats):
        """Generate an unknown host response"""
        stdout = output_formats["unknown_host_format"].format(address=address)
        returncode = output_formats["returncode_unknown_host"]
        return MockCompletedProcess(returncode, stdout)

    def _mock_timeout_ping(address, icmp_count, output_formats):
        """Generate a timeout response"""
        ip_address = address  # For timeout, use the address as IP
        ping_responses = ""
        if output_formats["timeout_response_line"]:
            for seq in range(1, icmp_count + 1):
                ping_responses += output_formats["timeout_response_line"].format(
                    ip_address=ip_address, seq=seq
                )

        stdout = output_formats["timeout_format"].format(
            icmp_count=icmp_count,
            address=address,
            ip_address=ip_address,
            ping_responses=ping_responses
        )
        returncode = output_formats["returncode_timeout"]
        return MockCompletedProcess(returncode, stdout)

    def _mock_partial_loss_ping(address, icmp_count, output_formats):
        """Generate a partial packet loss response"""
        ip_address = PARTIAL_LOSS_IP  # Mock IP for partial loss host
        received = max(1, icmp_count // 2)  # At least 1, about half lost
        lost = icmp_count - received
        loss_percent = (lost / icmp_count) * 100

        # Generate partial loss responses
        ping_responses = ""
        for seq in range(1, icmp_count + 1):
            # Only generate responses for packets that were received
            if seq <= received:
                rtt_time = RTT_AVG + ((seq - 1) * 0.005)
                ping_responses += output_formats["partial_loss_response_line"].format(
                    ip_address=ip_address, seq=seq, rtt_time=rtt_time
                )

        stdout = output_formats["partial_loss_format"].format(
            icmp_count=icmp_count,
            address=address,
            ip_address=ip_address,
            received=received,
            lost=lost,
            loss_percent=loss_percent,
            ping_responses=ping_responses
        )
        return MockCompletedProcess(0, stdout)

    def mock_execute_ping_command(address, icmp_count=1, timeout=1):
        """Main mock function that delegates to specific scenario handlers"""
        # Determine current platform or use a specified test platform
        current_platform = platform.system()

        # Fall back to Linux format if platform not recognized
        output_formats = PING_OUTPUT_FORMATS.get(
            current_platform, PING_OUTPUT_FORMATS["Linux"]
        )

        # Delegate based on the address
        if address == LOCALHOST_HOST or address == LOCALHOST_IP:
            return _mock_successful_ping(address, icmp_count, output_formats)
        elif address == UNKNOWN_HOST:
            return _mock_unknown_host(address, output_formats)
        elif address in TEST_NET_IPS:
            return _mock_timeout_ping(address, icmp_count, output_formats)
        elif address == PARTIAL_LOSS_HOST:
            return _mock_partial_loss_ping(address, icmp_count, output_formats)
        else:
            # Default fallback
            return _mock_timeout_ping(address, icmp_count, output_formats)

    # Replace the actual execution function with our mock
    monkeypatch.setattr(ping, "_execute_ping_command", mock_execute_ping_command)