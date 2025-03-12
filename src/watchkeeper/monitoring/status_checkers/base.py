from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class StatusCheckResult(ABC):
	is_up: bool | None
	timestamp: datetime
	error: bool = False


class StatusChecker(ABC):
	@classmethod
	@abstractmethod
	def check_status(cls, address: str, **kwargs: Any) -> StatusCheckResult:
		pass

	@staticmethod
	def _filter_kwargs(allowed_keys: list[str], **kwargs: Any) -> dict[str, Any]:
		"""
		Helper method to filter kwargs to only include keys in allowed_keys.

		Args:
			allowed_keys: List of parameter names to keep
			**kwargs: Arbitrary keyword arguments

		Returns:
			Dictionary containing only the allowed keyword arguments
		"""
		return {k: v for k, v in kwargs.items() if k in allowed_keys}
