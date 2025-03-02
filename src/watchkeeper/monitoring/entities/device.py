from dataclasses import dataclass
from datetime import datetime

from ...utils.ip_address import IPAddress
from ..status_checkers.base import (
	StatusChecker,
	StatusCheckResult,
)


@dataclass
class Device:
	name: str
	status_checker: StatusChecker
	ip_address: IPAddress
	__last_checked: datetime = None
	__last_updated: datetime = None
	__last_status: bool = None

	def __post_init__(self) -> None:
		_ = self.is_up

	@property
	def is_up(self) -> bool:
		check_result = self.status_checker.check_status(self.ip_address)
		self.__update(check_result)
		return check_result.is_up

	@property
	def last_update(self) -> datetime:
		return self.__last_updated

	def __update(self, check_result: StatusCheckResult) -> None:
		self.__last_checked = check_result.timestamp
		if self.__last_status != check_result.is_up:
			self.__last_updated = check_result.timestamp
			self.__last_status = check_result.is_up
