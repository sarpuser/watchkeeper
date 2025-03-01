from datetime import datetime

import pytest

from watchkeeper.monitoring.entities import Device
from watchkeeper.monitoring.status_checkers import (
	StatusChecker,
	StatusCheckResult,
)

NOW_TIME = datetime(2024, 1, 1, 12, 0, 0)
FIVE_MIN_AGO_TIME = datetime(2024, 1, 1, 11, 55, 0)
TEST_IP_ADDRESS = "TEST.IP.ADDRESS"


@pytest.fixture
def mock_status_checker() -> StatusChecker:
	class MockChecker(StatusChecker):
		def __init__(self, is_up: bool, timestamp: datetime):
			self.is_up = is_up
			self.timestamp = timestamp

		def check_status(self, address) -> StatusCheckResult:
			return StatusCheckResult(is_up=self.is_up, timestamp=self.timestamp)

	return MockChecker


@pytest.mark.parametrize(
	"is_up_expected",
	[True, False],
)
def test_device_up_status(mock_status_checker, is_up_expected):
	device = Device(
		"test_device",
		mock_status_checker(is_up=is_up_expected, timestamp=NOW_TIME),
		TEST_IP_ADDRESS,  # not testing
	)
	assert device.is_up == is_up_expected


def test_device_update_last_checked(mock_status_checker):
	device = Device(
		"test_device",
		mock_status_checker(is_up=True, timestamp=NOW_TIME),
		TEST_IP_ADDRESS,
		FIVE_MIN_AGO_TIME,  # last checked
	)
	_ = device.is_up  # The is_up property should update last checked
	assert device._Device__last_checked == NOW_TIME


@pytest.mark.parametrize(
	"is_up, last_status, expected_last_updated",
	[
		(False, False, FIVE_MIN_AGO_TIME),
		(False, True, NOW_TIME),
		(True, False, NOW_TIME),
		(True, True, FIVE_MIN_AGO_TIME),
	],
)
def test_device_update_last_updated(
	mock_status_checker, is_up, last_status, expected_last_updated
):
	device = Device(
		"test_device",
		mock_status_checker(is_up=is_up, timestamp=NOW_TIME),
		TEST_IP_ADDRESS,  # not testing
		NOW_TIME,  # last checked - not testing
		FIVE_MIN_AGO_TIME,  # last updated
		last_status,
	)
	_ = device.is_up  # is_up updates last updated if status changed
	assert device._Device__last_updated == expected_last_updated


@pytest.mark.parametrize(
	"last_status, is_up, expected_last_status",
	[
		(False, False, False),
		(False, True, True),
		(True, False, False),
		(True, True, True),
	],
)
def test_device_update_last_status(
	mock_status_checker, last_status, is_up, expected_last_status
):
	device = Device(
		"test_device",
		mock_status_checker(is_up=is_up, timestamp=NOW_TIME),
		TEST_IP_ADDRESS,  # not testing
		NOW_TIME,  # last checked - not testing
		NOW_TIME,  # last updated - not testing
		last_status,
	)
	_ = device.is_up  # is_up updates last updated if status changed
	assert device._Device__last_status == expected_last_status


def test_device_last_checked_after_init(mock_status_checker):
	device = Device(
		"test_device",
		mock_status_checker(is_up=False, timestamp=NOW_TIME),
		TEST_IP_ADDRESS,
	)
	assert device._Device__last_checked is not None
	assert device._Device__last_checked == NOW_TIME


def test_device_last_updated_after_init(mock_status_checker):
	device = Device(
		"test_device",
		mock_status_checker(is_up=False, timestamp=NOW_TIME),
		TEST_IP_ADDRESS,
	)
	assert device._Device__last_updated is not None
	assert device._Device__last_updated == NOW_TIME
