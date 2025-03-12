from typing import Any

from ..base import StatusChecker, StatusCheckResult
from .ping_command import PingStatus, ping


class PingChecker(StatusChecker):
	@classmethod
	def check_status(cls, address: str, **kwargs: Any) -> StatusCheckResult:
		# Filter kwargs to only include parameters that ping accepts
		ping_kwargs = cls._filter_kwargs(["icmp_count", "timeout"], **kwargs)

		is_up = None
		error = False
		result = ping(address, **ping_kwargs)

		if result.status == PingStatus.SUCCESS:
			is_up = True
		elif result.status in [PingStatus.UNKNOWN_HOST, PingStatus.TIMEOUT]:
			is_up = False
		else:
			error = True

		return StatusCheckResult(is_up, result.timestamp, error)
