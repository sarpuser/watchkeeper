from watchkeeper.monitoring.status_checkers import PingChecker, StatusCheckResult

from .values import (
	DUMMY_IP,
	EXECUTION_ERROR_HOST,
	LOCALHOST_HOST,
	MALFORMED_OUTPUT_HOST,
	TEST_NET_IPS,
	UNKNOWN_HOST,
)


def test_ping_checker_success(mock_ping_command):
	"""Test that a successful ping returns a successful status check result."""
	result = PingChecker.check_status(LOCALHOST_HOST)

	assert isinstance(result, StatusCheckResult)
	assert result.is_up is True
	assert result.timestamp is not None
	assert result.error is False


def test_ping_checker_timeout(mock_ping_command):
	"""Test that a ping timeout returns a status check result with is_up=False."""
	result = PingChecker.check_status(TEST_NET_IPS[0])

	assert isinstance(result, StatusCheckResult)
	assert result.is_up is False
	assert result.timestamp is not None
	assert result.error is False


def test_ping_checker_unknown_host(mock_ping_command):
	"""Test that an unknown host returns a status check result with is_up=False."""
	result = PingChecker.check_status(UNKNOWN_HOST)

	assert isinstance(result, StatusCheckResult)
	assert result.is_up is False
	assert result.timestamp is not None
	assert result.error is False


def test_ping_checker_network_error(mock_ping_command):
	"""Test that a network error returns a status check result with error=True."""
	result = PingChecker.check_status(DUMMY_IP)

	assert isinstance(result, StatusCheckResult)
	assert result.is_up is None
	assert result.timestamp is not None
	assert result.error is True


def test_ping_checker_parse_error(mock_ping_command):
	"""Test that a parse error returns a status check result with error=True."""
	result = PingChecker.check_status(MALFORMED_OUTPUT_HOST)

	assert isinstance(result, StatusCheckResult)
	assert result.is_up is None
	assert result.timestamp is not None
	assert result.error is True


def test_ping_checker_with_kwargs(mock_ping_command):
	"""Test that kwargs are correctly passed to the ping function."""
	result = PingChecker.check_status(
		LOCALHOST_HOST, icmp_count=5, timeout=3, ignored_param="value"
	)

	assert isinstance(result, StatusCheckResult)
	assert result.is_up is True
	assert result.error is False


def test_ping_checker_execution_error(mock_ping_command):
	"""Test that a command execution error returns a status check result with error=True."""

	result = PingChecker.check_status(EXECUTION_ERROR_HOST)

	assert isinstance(result, StatusCheckResult)
	assert result.is_up is None
	assert result.timestamp is not None
	assert result.error is True
