import pytest

from tests.base import Factory
from utilities.error_handling import InvalidComponent, DuplicateComponent, InconsistentProduct


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


