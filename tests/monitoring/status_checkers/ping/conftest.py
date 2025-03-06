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
		stdout = (
			output_formats["output_format"].format(
				icmp_count=icmp_count,
				address=address,
				ip_address=ip_address,
				received=icmp_count,
				loss_percent=0,
				ping_responses=ping_responses,
			)
			+ output_formats["rtt_summary_line"]
		)
		return MockCompletedProcess(0, stdout)

	def _mock_unknown_host(address, output_formats):
		"""Generate an unknown host response"""
		stdout = output_formats["unknown_host_format"].format(address=address)
		returncode = output_formats["unknown_host_returncode"]
		return MockCompletedProcess(returncode, stdout)

	def _mock_timeout_ping(address, icmp_count, output_formats):
		"""Generate a timeout response"""
		ip_address = address  # For timeout, use the address as IP
		ping_responses = _generate_ping_responses(
			address, icmp_count, output_formats["timeout_response_line"]
		)
		# if output_formats["timeout_response_line"]:
		#     for seq in range(1, icmp_count + 1):
		#         ping_responses += output_formats["timeout_response_line"].format(
		#             ip_address=ip_address, seq=seq
		#         )

		stdout = output_formats["output_format"].format(
			icmp_count=icmp_count,
			address=address,
			ip_address=ip_address,
			received=0,
			loss_percent=100,
			ping_responses=ping_responses,
		)
		returncode = output_formats["timeout_returncode"]
		return MockCompletedProcess(returncode, stdout)

	def _mock_partial_loss_ping(address, icmp_count, output_formats):
		"""Generate a partial packet loss response"""
		ip_address = PARTIAL_LOSS_IP  # Mock IP for partial loss host
		received = max(1, icmp_count // 2)  # At least 1, about half lost
		lost = icmp_count - received
		loss_percent = (lost / icmp_count) * 100

		# Generate partial loss responses
		ping_responses = _generate_ping_responses(
			address, received, output_formats["success_response_line"]
		) + _generate_ping_responses(
			address, lost, output_formats["timeout_response_line"]
		)

		stdout = (
			output_formats["output_format"].format(
				icmp_count=icmp_count,
				address=address,
				ip_address=ip_address,
				received=received,
				lost=lost,
				loss_percent=loss_percent,
				ping_responses=ping_responses,
			)
			+ output_formats["rtt_summary_line"]
		)
		return MockCompletedProcess(0, stdout)

	def mock_execute_ping_command(address, icmp_count=1, timeout=1):
		"""Main mock function that delegates to specific scenario handlers"""

		# Delegate based on the address
		if address == LOCALHOST_HOST or address == LOCALHOST_IP:
			return _mock_successful_ping(address, icmp_count, PING_OUTPUT_FORMATS)
		elif address == UNKNOWN_HOST:
			return _mock_unknown_host(address, PING_OUTPUT_FORMATS)
		elif address in TEST_NET_IPS:
			return _mock_timeout_ping(address, icmp_count, PING_OUTPUT_FORMATS)
		elif address == PARTIAL_LOSS_HOST:
			return _mock_partial_loss_ping(address, icmp_count, PING_OUTPUT_FORMATS)
		else:
			# Default fallback
			return _mock_timeout_ping(address, icmp_count, PING_OUTPUT_FORMATS)

	# Replace the actual execution function with our mock
	monkeypatch.setattr(ping, "_execute_ping_command", mock_execute_ping_command)
