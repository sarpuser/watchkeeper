from watchkeeper.monitoring.status_checkers.base import StatusChecker


class TestStatusCheckerFilterKwargs:
	def test_filter_kwargs_all_allowed(self):
		"""Test when all keys are in the allowed list."""
		allowed_keys = ["param1", "param2", "param3"]
		test_kwargs = {"param1": "value1", "param2": 42, "param3": True}

		result = StatusChecker._filter_kwargs(allowed_keys, **test_kwargs)

		assert result == test_kwargs
		assert len(result) == 3

	def test_filter_kwargs_some_allowed(self):
		"""Test when only some keys are in the allowed list."""
		allowed_keys = ["param1", "param3"]
		test_kwargs = {"param1": "value1", "param2": 42, "param3": True, "param4": []}

		result = StatusChecker._filter_kwargs(allowed_keys, **test_kwargs)

		assert result == {"param1": "value1", "param3": True}
		assert len(result) == 2
		assert "param2" not in result
		assert "param4" not in result

	def test_filter_kwargs_none_allowed(self):
		"""Test when no keys are in the allowed list."""
		allowed_keys = ["param5", "param6"]
		test_kwargs = {"param1": "value1", "param2": 42, "param3": True}

		result = StatusChecker._filter_kwargs(allowed_keys, **test_kwargs)

		assert result == {}
		assert len(result) == 0

	def test_filter_kwargs_empty_allowed(self):
		"""Test with an empty allowed keys list."""
		allowed_keys = []
		test_kwargs = {"param1": "value1", "param2": 42, "param3": True}

		result = StatusChecker._filter_kwargs(allowed_keys, **test_kwargs)

		assert result == {}
		assert len(result) == 0

	def test_filter_kwargs_empty_kwargs(self):
		"""Test with empty kwargs."""
		allowed_keys = ["param1", "param2", "param3"]

		result = StatusChecker._filter_kwargs(allowed_keys)

		assert result == {}
		assert len(result) == 0

	def test_filter_kwargs_value_types(self):
		"""Test that the method preserves various value types."""
		allowed_keys = ["string", "number", "boolean", "list", "dict", "none"]
		test_kwargs = {
			"string": "value",
			"number": 42,
			"boolean": True,
			"list": [1, 2, 3],
			"dict": {"key": "value"},
			"none": None,
			"excluded": "not allowed",
		}

		result = StatusChecker._filter_kwargs(allowed_keys, **test_kwargs)

		assert result == {
			"string": "value",
			"number": 42,
			"boolean": True,
			"list": [1, 2, 3],
			"dict": {"key": "value"},
			"none": None,
		}
		assert len(result) == 6
		assert "excluded" not in result
