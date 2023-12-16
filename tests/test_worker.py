import pytest

from main import run_simulation
from tests.base import Factory
from utilities.error_handling import InconsistentProduct


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
