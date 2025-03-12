import re
import subprocess  # nosec B404
from dataclasses import KW_ONLY, dataclass
from datetime import datetime
from enum import Enum

from ....utils.ip_address import IPAddress

DEFAULT_ICMP_COUNT = 2
DEFAULT_TIMEOUT = 1


class PingStatus(Enum):
	SUCCESS = 0
	TIMEOUT = 1
	UNKNOWN_HOST = 2
	PARSE_ERROR = 3
	EXECUTION_ERROR = 4
	NETWORK_ERROR = 5
	COMMAND_ERROR = 6


@dataclass
class PingResult:
	hostname: str
	ip_address: IPAddress | None
	_: KW_ONLY
	packets_sent: int = 0
	packets_received: int = 0
	packet_loss: float = 0
	rtt_min: float = 0
	rtt_avg: float = 0
	rtt_max: float = 0
	rtt_std_dev: float = 0
	status: PingStatus
	timestamp: datetime = None

	def __post_init__(self) -> None:
		self.timestamp = datetime.now()


def ping(
	address: str,
	*,
	icmp_count: int = DEFAULT_ICMP_COUNT,
	timeout: int = DEFAULT_TIMEOUT,
) -> PingResult:
	try:
		process_result = _execute_ping_command(address, icmp_count, timeout)
		return _parse_output(process_result)
	except subprocess.SubprocessError:
		return PingResult(address, None, status=PingStatus.EXECUTION_ERROR)
	except ValueError:
		return PingResult(address, None, status=PingStatus.COMMAND_ERROR)


def _execute_ping_command(
	address: str, icmp_count: int, timeout: int
) -> subprocess.CompletedProcess:
	if icmp_count < 1 or timeout < 1:
		raise ValueError("ping: count of packets to transmit must be greater than 1")
	if timeout < 1:
		raise ValueError("ping: timeout must be greater than 1")
	return subprocess.run(  # nosec B404
		["ping", "-c", str(icmp_count), "-W", str(timeout), address],
		capture_output=True,
	)


def _parse_output(process_result: subprocess.CompletedProcess) -> PingResult:
	stdout = process_result.stdout.decode()
	stderr = process_result.stderr.decode()
	output = stdout if stdout else stderr

	address = process_result.args[-1]
	if "Unknown host" in output:
		return PingResult(address, None, status=PingStatus.UNKNOWN_HOST)

	output_lines = output[:-1].split("\n")

	ip_address_match = re.search(r"((\d{1,3}\.){3}\d{1,3})", output_lines[0])
	if ip_address_match is None:
		return PingResult(address, None, status=PingStatus.PARSE_ERROR)

	ip_address = IPAddress(ip_address_match[1])

	packet_summary = (
		output_lines[-2] if "min/avg/max" in output_lines[-1] else output_lines[-1]
	)

	packets_sent = int(re.search(r"(\d+) packets transmitted", packet_summary)[1])
	packets_received = int(re.search(r"(\d+) packets received", packet_summary)[1])
	packet_loss = float(re.search(r"([\d\.]+)% packet loss", packet_summary)[1])

	if "No route to host" in output_lines[1]:
		return PingResult(
			address,
			ip_address,
			packets_sent=packets_sent,
			packets_received=packets_received,
			packet_loss=packet_loss,
			status=PingStatus.NETWORK_ERROR,
		)

	if packets_received == 0:
		return PingResult(
			address,
			ip_address,
			packets_sent=packets_sent,
			packets_received=packets_received,
			packet_loss=packet_loss,
			status=PingStatus.TIMEOUT,
		)

	rtt_summary = output_lines[-1]
	rtt_values = re.search(r" (([\d\.]+/){3}[\d\.]+) ms", rtt_summary)[1].split("/")
	rtt_min = float(rtt_values[0])
	rtt_avg = float(rtt_values[1])
	rtt_max = float(rtt_values[2])
	rtt_std_dev = float(rtt_values[3])
	error = PingStatus.SUCCESS

	return PingResult(
		address,
		ip_address,
		packets_sent=packets_sent,
		packets_received=packets_received,
		packet_loss=packet_loss,
		rtt_min=rtt_min,
		rtt_avg=rtt_avg,
		rtt_max=rtt_max,
		rtt_std_dev=rtt_std_dev,
		status=error,
	)
