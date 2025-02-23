from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime


@dataclass
class StatusResult(ABC):
	is_up: bool
	timestamp: datetime


class StatusChecker(ABC):
	@abstractmethod
	def check_status(self) -> StatusResult:
		pass
