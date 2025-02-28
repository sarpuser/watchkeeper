# Test addresses
LOCALHOST_HOST = "localhost"
LOCALHOST_IP = "127.0.0.1"
UNKNOWN_HOST = "invalid.host.test"
TEST_NET_IPS = ["192.0.2.0", "198.51.100.0", "203.0.113.0"]
PARTIAL_LOSS_HOST = "partial.loss.test"
PARTIAL_LOSS_IP = "192.168.0.1" # Doesn't really matter

# Default RTT values
RTT_MIN = 0.020
RTT_AVG = 0.048
RTT_MAX = 0.096
RTT_STD_DEV = 0.029

# Define platform-specific output formats as a dictionary
PING_OUTPUT_FORMATS = {
    "Linux": {
        "success_format": (
            "PING {address} ({ip_address}) 56(84) bytes of data.\n"
            "{ping_responses}"
            "{icmp_count} packets transmitted, {icmp_count} received, 0% packet loss, time 4ms\n"
            f"rtt min/avg/max/mdev = {RTT_MIN}/{RTT_AVG}/{RTT_MAX}/{RTT_STD_DEV} ms"
        ),
        "success_response_line": "64 bytes from {ip_address}: icmp_seq={seq} ttl=64 time={rtt_time:.3f} ms\n",
        "timeout_format": (
            "PING {address} ({ip_address}) 56(84) bytes of data.\n"
            "{ping_responses}"
            "{icmp_count} packets transmitted, 0 received, 100% packet loss, time 4ms"
        ),
        "timeout_response_line": "",  # No responses for timeout
        "partial_loss_format": (
            "PING {address} ({ip_address}) 56(84) bytes of data.\n"
            "{ping_responses}"
            "{icmp_count} packets transmitted, {received} received, {loss_percent:.1f}% packet loss, time 4ms\n"
            f"rtt min/avg/max/mdev = {RTT_MIN:.3f}/{RTT_AVG:.3f}/{RTT_MAX:.3f}/{RTT_STD_DEV:.3f} ms"
        ),
        "partial_loss_response_line": "64 bytes from {ip_address}: icmp_seq={seq} ttl=64 time={rtt_time:.3f} ms\n",
        "unknown_host_format": "ping: unknown host {address}",
        "returncode_unknown_host": 2,
        "returncode_timeout": 1,
    },
    "Windows": {
        "success_format": (
            "Pinging {address} [{ip_address}] with 32 bytes of data:\n"
            "{ping_responses}"
            "Ping statistics for {ip_address}:\n"
            "    Packets: Sent = {icmp_count}, Received = {icmp_count}, Lost = 0 (0% loss),\n"
            "Approximate round trip times in milli-seconds:\n"
            f"    Minimum = {RTT_MIN}ms, Maximum = {RTT_MAX}ms, Average = {RTT_AVG}ms\n"
        ),
        "success_response_line": "Reply from {ip_address}: bytes=32 time={rtt_time:.0f}ms TTL=64\n",
        "timeout_format": (
            "Pinging {address} [{ip_address}] with 32 bytes of data:\n"
            "{ping_responses}"
            "Ping statistics for {ip_address}:\n"
            "    Packets: Sent = {icmp_count}, Received = 0, Lost = {icmp_count} (100% loss)"
        ),
        "timeout_response_line": "Request timed out.\n",
        "partial_loss_format": (
            "Pinging {address} [{ip_address}] with 32 bytes of data:\n"
            "{ping_responses}"
            "Ping statistics for {ip_address}:\n"
            "    Packets: Sent = {icmp_count}, Received = {received}, Lost = {lost} ({loss_percent:.0f}% loss),\n"
            "Approximate round trip times in milli-seconds:\n"
            f"    Minimum = {RTT_MIN}ms, Maximum = {RTT_MAX}ms, Average = {RTT_AVG}ms"
        ),
        "partial_loss_response_line": "Reply from {ip_address}: bytes=32 time={rtt_time:.0f}ms TTL=64\n",
        "unknown_host_format": "Ping request could not find host {address}. Please check the name and try again.",
        "returncode_unknown_host": 1,
        "returncode_timeout": 1,
    },
    "Darwin": {  # macOS
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
    },
}