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
def create_mock_checker_class():
	"""Returns a function that creates mock status checker classes"""

	def _create_class(is_up: bool, timestamp: datetime, error=False) -> type:
		class MockCheckerClass(StatusChecker):
			@classmethod
			def check_status(cls, address, **kwargs) -> StatusCheckResult:
				return StatusCheckResult(is_up=is_up, timestamp=timestamp, error=error)

		return MockCheckerClass

	return _create_class


@pytest.mark.parametrize(
	"is_up_expected",
	[True, False],
)
def test_device_up_status(create_mock_checker_class, is_up_expected):
	mock_status_checker = create_mock_checker_class(is_up_expected, NOW_TIME)

	device = Device(
		"test_device",
		mock_status_checker,
		TEST_IP_ADDRESS,  # not testing
	)
	assert device.is_up == is_up_expected


def test_device_update_last_checked(create_mock_checker_class):
	mock_status_checker = create_mock_checker_class(True, NOW_TIME)

	device = Device(
		"test_device",
		mock_status_checker,
		TEST_IP_ADDRESS,
	)
	device._Device__last_checked = FIVE_MIN_AGO_TIME
	_ = device.is_up  # The is_up property should update last checked
	assert device.last_checked == NOW_TIME


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
	create_mock_checker_class, is_up, last_status, expected_last_updated
):
	mock_status_checker = create_mock_checker_class(is_up, NOW_TIME)

	device = Device(
		"test_device",
		mock_status_checker,
		TEST_IP_ADDRESS,  # not testing
	)
	device._Device__last_updated = FIVE_MIN_AGO_TIME
	device._Device__last_status = last_status
	_ = device.is_up  # is_up updates last updated if status changed
	assert device.last_update == expected_last_updated


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
	create_mock_checker_class, last_status, is_up, expected_last_status
):
	mock_status_checker = create_mock_checker_class(is_up, NOW_TIME)

	device = Device(
		"test_device",
		mock_status_checker,
		TEST_IP_ADDRESS,  # not testing
	)
	device._Device__last_status = last_status
	_ = device.is_up  # is_up updates last updated if status changed
	assert device._Device__last_status == expected_last_status


def test_device_last_checked_after_init(create_mock_checker_class):
	mock_status_checker = create_mock_checker_class(False, NOW_TIME)

	device = Device(
		"test_device",
		mock_status_checker,
		TEST_IP_ADDRESS,
	)
	assert device.last_checked is not None
	assert device.last_checked == NOW_TIME


def test_device_last_updated_after_init(create_mock_checker_class):
	mock_status_checker = create_mock_checker_class(False, NOW_TIME)

	device = Device(
		"test_device",
		mock_status_checker,
		TEST_IP_ADDRESS,
	)
	assert device.last_update is not None
	assert device.last_update == NOW_TIME


@pytest.mark.parametrize(
	"error, is_up, last_status, expected_is_up",
	[
		(True, None, True, True),
		(True, None, False, False),
		(False, True, False, True),
		(False, False, True, False),
	],
)
def test_device_check_error_returns_last_status(
	create_mock_checker_class, error, is_up, last_status, expected_is_up
):
	mock_status_checker = create_mock_checker_class(is_up, NOW_TIME, error)

	device = Device("test_device", mock_status_checker, TEST_IP_ADDRESS)
	device._Device__last_status = last_status

	assert device.is_up == expected_is_up
