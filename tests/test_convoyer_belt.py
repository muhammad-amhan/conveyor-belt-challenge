import re

import pytest

from main import ConveyorBelt, Worker, Product, run_simulation
from utilities.error_handling import InvalidComponent, DuplicateComponent, InconsistentProduct


class Factory:
    def __init__(
            self,
            belt_length=3,
            belt_iterations=100,
            finished_product='P',
            assembly_time=0,
            workers_per_slot=1,
            belt_speed=0,
            item_interval_range=0,
            debug=False,
    ):
        self.belt_length = belt_length
        self.belt_iterations = belt_iterations
        self.belt_speed = belt_speed
        self.finished_product = finished_product
        self.assembly_time = assembly_time
        self.workers_per_slot = workers_per_slot
        self.item_interval_range = item_interval_range
        self.debug = debug

        self.product = Product(
            items=['A', 'B', 'C', 'D', 'E', 'F', None],
            components=['A', 'B', 'C'],
            finished_product=self.finished_product,
            item_interval_range=self.item_interval_range,
        )
        self.belt = ConveyorBelt(self.belt_length, self.product, self.belt_iterations, self.belt_speed)

        self.workers = [
            [Worker(self.belt, self.product) for _ in range(self.workers_per_slot)]
            for _ in range(self.belt_length)
        ]


class TestProduct:
    @pytest.fixture
    def factory(self):
        factory = Factory()
        yield factory

    def test_product_is_not_allowed_in_components(self, factory):
        finished_product = 'P'
        factory.finished_product = finished_product
        factory.product.finished_product = finished_product
        factory.product.components.append(finished_product)

        with pytest.raises(InvalidComponent):
            assert f'Component "{finished_product}" is wasting worker' in factory.product.validate_supplied_components()

    def test_invalid_component_character_type(self, factory):
        invalid_components = ['', '?', '#', ' ']

        for component in invalid_components:
            with pytest.raises(InvalidComponent) as e:
                factory.product.components.append(component)
                factory.product.validate_supplied_components()
                assert f'Component "{component}" is invalid' in e.value.args[0]

            factory.product.components.pop()

    def test_component_cannot_be_none(self, factory):
        factory.product.components.append(None)

        with pytest.raises(InvalidComponent):
            assert 'Supplied an empty component' in factory.product.validate_supplied_components()

    def test_component_must_be_singular(self, factory):
        factory.product.items.append('AC')
        factory.product.components.append('AC')
        with pytest.raises(InvalidComponent):
            assert 'Component "AC" must be singular' in factory.product.validate_supplied_components()

    def test_reject_component_if_not_supplied_in_item(self, factory):
        components = ['F', 'G']
        factory.product.components = components
        with pytest.raises(InvalidComponent):
            assert 'Component "G" is not recognized' in factory.product.validate_supplied_components()

        factory.product.items.extend(['G'])
        factory.product.validate_supplied_components()

    def test_valid_components(self, factory):
        valid_components = ['2', 'S']
        factory.product.items.extend(valid_components)
        factory.product.components.extend(valid_components)
        factory.product.validate_supplied_components()

    def test_reject_duplicate_component(self, factory):
        component = 'A'
        factory.product.components.extend(component)
        with pytest.raises(DuplicateComponent):
            assert f'Component "{component}" is duplicate' in factory.product.validate_supplied_components()


class TestWorker:
    @pytest.fixture
    def factory(self):
        factory = Factory()
        yield factory

    def test_valid_assembled_product_combinations(self, factory):
        product_combinations = run_simulation(factory.belt, factory.workers)

        for product_combination in product_combinations:
            assert len(product_combination) == len(factory.product.components)
            for component in product_combination:
                assert component in factory.product.components

    def test_worker_ignores_unwanted_components(self, factory):
        finished_product = factory.product.finished_product
        worker = factory.workers[0][0]
        picked = worker.pick_item(finished_product)
        assert not picked

        not_in_components = 'X'
        picked = worker.pick_item(not_in_components)
        assert not picked

    def test_assemble_intermediate_product_success(self, factory):
        worker = factory.workers[0][0]
        worker.left_hand = 'A'
        worker.right_hand = 'B'
        intermediate_product = 'AB'
        worker.assemble()

        assert worker.left_hand == intermediate_product
        assert worker.right_hand is None

    def test_assemble_finished_product_success(self, factory):
        worker = factory.workers[0][0]
        worker.left_hand = 'AB'
        worker.right_hand = 'C'
        product_combination = 'ABC'
        worker.assemble()

        assert worker.left_hand == product_combination
        assert worker.right_hand is None

    def test_worker_holds_valid_finished_product(self, factory):
        worker = factory.workers[0][0]
        worker.left_hand = 'ABC'
        assert worker.assembled_finished_product() is True

    def test_worker_holds_invalid_finished_product(self, factory):
        worker = factory.workers[0][0]
        worker.left_hand = 'AB'
        assert worker.assembled_finished_product() is False

        inconsistent_products = ['ABB', 'AFB', 'ABCB', 'ABCD']
        for product in inconsistent_products:
            worker.left_hand = product
            with pytest.raises(InconsistentProduct) as e:
                assert f'Inconsistent product "{product}" by worker "{worker.worker_id}"' in worker.assembled_finished_product()


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
