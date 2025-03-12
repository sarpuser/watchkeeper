# Test addresses
LOCALHOST_HOST = "localhost"
LOCALHOST_IP = "127.0.0.1"
UNKNOWN_HOST = "invalid.host.test"
TEST_NET_IPS = ["192.0.2.0", "198.51.100.0", "203.0.113.0"]
PARTIAL_LOSS_HOST = "partial.loss.test"
DUMMY_IP = "192.168.0.1"  # Doesn't really matter
MALFORMED_OUTPUT_HOST = "malformed.output.test"
EXECUTION_ERROR_HOST = "execution.error.test"

# Default RTT values
RTT_MIN = 0.020
RTT_AVG = 0.048
RTT_MAX = 0.096
RTT_STD_DEV = 0.029

# Define platform-specific output formats as a dictionary
PING_OUTPUT_FORMATS = {
	"output_format": (
		"PING {address} ({ip_address}): 56 data bytes\n"
		"{ping_responses}"
		"\n--- {address} ping statistics ---\n"
		"{icmp_count} packets transmitted, {received} packets received, {loss_percent}% packet loss\n"
	),
	"rtt_summary_line": f"round-trip min/avg/max/stddev = {RTT_MIN:.3f}/{RTT_AVG:.3f}/{RTT_MAX:.3f}/{RTT_STD_DEV:.3f} ms\n",
	"success_response_line": "64 bytes from {ip_address}: icmp_seq={seq} ttl=64 time={rtt_time:.3f} ms\n",
	"timeout_response_line": "Request timeout for icmp_seq {seq}\n",
	"unknown_host_format": "ping: cannot resolve {address}: Unknown host",
	"unknown_host_returncode": 2,
	"timeout_returncode": 2,
	"network_unreachable_response_line": "ping: sendto: No route to host",
	"network_unreachable_returncode": 68,
}
