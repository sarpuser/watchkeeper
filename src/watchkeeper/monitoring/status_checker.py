from abc import ABC, abstractmethod


class StatusChecker(ABC):
	@abstractmethod
	def check_status(self) -> dict:
		pass
