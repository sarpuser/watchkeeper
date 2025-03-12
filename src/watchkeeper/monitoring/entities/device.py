from datetime import datetime
from typing import Any

from ...utils.ip_address import IPAddress
from ..status_checkers.base import (
	StatusChecker,
	StatusCheckResult,
)


class Device:
	def __init__(
		self,
		name: str,
		status_checker_cls: StatusChecker,
		ip_address: IPAddress,
		**kwargs: Any,
	) -> None:
		self.name = name
		self.status_checker_cls = status_checker_cls
		self.ip_address = ip_address
		self.checker_kwargs = kwargs
		self.__last_checked: datetime = None
		self.__last_updated: datetime = None
		self.__last_status: bool = None

		_ = self.is_up

	@property
	def is_up(self) -> bool | None:
		check_result = self.status_checker_cls.check_status(
			self.ip_address, **self.checker_kwargs
		)
		self.__update(check_result)
		return check_result.is_up if not check_result.error else self.__last_status

	@property
	def last_update(self) -> datetime:
		return self.__last_updated

	@property
	def last_checked(self) -> datetime:
		return self.__last_checked

	def __update(self, check_result: StatusCheckResult) -> None:
		self.__last_checked = check_result.timestamp
		if check_result.is_up is not None and self.__last_status != check_result.is_up:
			self.__last_updated = check_result.timestamp
			self.__last_status = check_result.is_up
