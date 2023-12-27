import pytest
from jsonschema import ValidationError
from jsonschema.validators import validate

from config.schema import BELT_SCHEMA
from tests.base import Factory


INVALID_CONFIGS = [
    {
        "belt": {
            "belt_delay": 1,
            "belt_iterations": 100
        },
        "workers_per_slot": 2,
        "finished_product": "P",
        "assembly_time": 3
    },
    {
        "debug": True,
        "belt": {
            "belt_length": 5,
            "belt_delay": 1,
            "belt_iterations": 100
        },
        "finished_product": "P",
        "assembly_time": 3
    },
    {
        "debug": False,
        "belt": {
            "belt_length": 5,
            "belt_delay": 1,
            "belt_iterations": 100
        },
        "workers_per_slot": 2,
        "finished_product": "P",
    },
    {
        "belt": {
            "belt_length": "5",
            "belt_delay": 1,
            "belt_iterations": 100
        },
        "workers_per_slot": 2,
        "finished_product": "P",
        "assembly_time": 3
    },
    {
        "belt": {
            "belt_length": 5,
            "belt_delay": 1,
            "belt_iterations": 100
        },
        "workers_per_slot": 2,
        "finished_product": 00000,
        "assembly_time": 3
    },
    {
        "workers_per_slot": 2,
        "finished_product": "P",
        "assembly_time": 3
    },
]

VALID_CONFIGS = [
    {
        "belt": {
            "belt_length": 5,
            "belt_delay": 1,
            "belt_iterations": 100
        },
        "workers_per_slot": 2,
        "finished_product": "P",
        "assembly_time": 3
    },
    {
        "debug": True,
        "belt": {
            "belt_length": 5,
            "belt_delay": 1,
            "belt_iterations": 100
        },
        "workers_per_slot": 2,
        "finished_product": "P",
        "assembly_time": 3
    },
]


class TestWorker:
    @pytest.fixture
    def factory(self):
        factory = Factory()
        yield factory

    def test_invalid_belt_configs(self, factory):
        for config in INVALID_CONFIGS:
            with pytest.raises(ValidationError) as e:
                validate(instance=config, schema=BELT_SCHEMA)
                assert "Invalid Belt Config" in e.message

    def test_valid_belt_configs(self, factory):
        for config in VALID_CONFIGS:
            validate(instance=config, schema=BELT_SCHEMA)