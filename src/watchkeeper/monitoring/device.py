from dataclasses import dataclass
from datetime import datetime
from watchkeeper.monitoring.status_checker import StatusChecker


@dataclass
class Device:
	name: str
	ip_address: str
	last_alive: datetime
	status_checker: StatusChecker

	@property
	def down_time(self) -> datetime:
		pass

	@property
	def is_up(self) -> bool:
		pass
