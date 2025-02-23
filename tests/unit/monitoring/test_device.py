from watchkeeper.monitoring.device import Device
from watchkeeper.monitoring.status_checker import StatusChecker, StatusResult
from datetime import datetime, timedelta
import pytest


NOW_TIME = datetime(2024, 1, 1, 12, 0, 0)
FIVE_MIN_AGO_TIME = datetime(2024, 1, 1, 11, 55, 0)
TEST_IP_ADDRESS = "TEST.IP.ADDRESS"


@pytest.fixture
def mock_status_checker() -> StatusChecker:
	class MockChecker(StatusChecker):
		def __init__(self, is_up: bool, timestamp: datetime):
			self.is_up = is_up
			self.timestamp = timestamp

		def check_status(self) -> StatusResult:
			return StatusResult(is_up=self.is_up, timestamp=self.timestamp)

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


@pytest.mark.parametrize(
	"last_updated,expected_duration",
	[
		(NOW_TIME, timedelta(minutes=0)),
		(FIVE_MIN_AGO_TIME, timedelta(minutes=5)),
	],
)
def test_device_status_duration(mock_status_checker, last_updated, expected_duration):
	device = Device(
		"test_device",
		mock_status_checker(
			is_up=True,  # not testing
			timestamp=NOW_TIME,
		),
		TEST_IP_ADDRESS,  # not testing
		NOW_TIME,  # last checked - not testing
		last_updated,  # last updated
	)
	assert device.status_duration == expected_duration


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
	"is_up, last_status, expected_last_status",
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
