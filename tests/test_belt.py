import pytest

from main import run_simulation
from tests.base import Factory


class TestBelt:
    @pytest.fixture
    def factory(self):
        factory = Factory()
        yield factory

    def test_iterations_match_the_data_counters(self, factory):
        belt = factory.belt
        workers = factory.workers
        iterations = belt.belt_iterations
        run_simulation(belt, workers)

        sum_of_data_counters = sum(belt.unpicked_components_counter.values()) + sum(belt.finished_products_counter.values())
        assert iterations == sum_of_data_counters
