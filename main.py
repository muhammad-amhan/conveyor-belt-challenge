"""
Assumptions:
1) Items can come into the belt at random intervals
    - Set the random interval to be between 1 and 5 seconds
    - For speed, I have set it to 0
2) Each slot can hold one component or a finished product (P - bound to user input) or nothing
3) Each slot has two workers
    - I have made it that each slot can have a dynamic number of workers bound to user input
4) Every 1 second, the belt moves one position
    - For speed, I have made it 0 seconds
5) Each worker can either pick a component or place a finished product onto the slot (one worker operates on each slot)
6) It takes 3 seconds to assemble an intermediate product or a final product
    - This means some components will be passing without being picked up
    - I have made that 1 second for speed
7) During the 1-second assembly time, workers can't interact with the belt
    - Workers can remain holding any two of (component, intermediate product, or a finished product) at a time in each
     hand e.g. (BC, A) or (None, C) or (None, A), or (P, None)
8) There should be an equal chance of any items to enter the belt
9) If a worker constructed an intermediate product, look only for the missing final component
10) The intermediate product is always assembled and placed in the worker's left hand
    - e.g. ('A', 'B') -> ('AB', None) -> found C -> pick C -> ('AB', 'C') -> ('P', None)
    - When a final component is found it should be picked by the right hand, then assembled in the left hand
      as presented above
11) A unit of time is defined as any number (e.g. 1) in seconds
"""

from random import choice, uniform
from time import sleep
from typing import Union, Dict, List
from timeit import default_timer as timer

from utilities.error_handling import EmptySlotRequired, InvalidComponent, DuplicateComponent, AssemblyError
from utilities.logger import Logger

ERROR_CODE = 1
SUCCESS_CODE = 0
log = Logger()


class Product:
    def __init__(self, items: List[Union[str, None]], components: List[str], finished_product: str):
        """
        A class that defined wha a product is made up of, how often it enters the belt, and what goes onto its slots.

        :param items: A list of singular alphanumerical characters e.g. ['A', 'B', '1', '2'].
        :param components: A list of all components and any other special or alphanumerical or empty characters.
        :param finished_product: A combination of all components mark a finished product
                 e.g. AB12, 1BA2, B2A1 => maps to a value on the belt to mark what the finished product should look like
        """
        self.item_interval = self.get_random_number(0, 0)
        self.items = items
        self.components = components
        self.finished_product = finished_product
        self.assembled_products = []
        # TODO
        #  Later improvement: this variable will be used to allow multi-character component instead of strictly singular
        self.product_combination_length = len(''.join(self.components))

    def validate_empty_slot(self):
        if None not in self.items:
            raise EmptySlotRequired(f'An empty slot is required for releasing a finished product.')

    def validate_supplied_components(self):
        if not self.finished_product.isalnum():
            raise ValueError(f'Finished product "{self.finished_product}" is invalid.')

        for component in self.components:
            if component is None:
                raise InvalidComponent(f'Supplied an empty component(s).')
            if not component.isalnum():
                raise InvalidComponent(f'Component type "{component}" is invalid.')
            if len(component) != 1:
                raise InvalidComponent(f'Component "{component}" must be singular')
            if component == self.finished_product:
                raise InvalidComponent(f'Component "{component}" is wasting the workers\' time.')
            if component not in self.items:
                raise InvalidComponent(f'Component "{component}" is not recognized. Please check supplied items.')
            if len([comp for comp in self.components if comp == component]) != 1:
                raise DuplicateComponent(f'Component "{component}" is duplicate.')

    def validate(self):
        try:
            self.validate_supplied_components()
            self.validate_empty_slot()
        except InvalidComponent as e:
            log.error(e)
            exit(ERROR_CODE)
        except EmptySlotRequired as e:
            log.error(e)
            exit(ERROR_CODE)
        except DuplicateComponent as e:
            log.error(e)
            exit(ERROR_CODE)

    @staticmethod
    def get_random_number(x: int = 0, y: int = 0):
        return uniform(x, y)

    def get_item_randomly(self) -> str:
        sleep(self.item_interval)
        return choice(self.items)


class ConveyorBelt:
    assembled_products_combination = []

    def __init__(self, belt_length: int, product: Product):
        """
        The belt will pass components, other items, including empty slots.
        :param belt_length: The length of the belt i.e. number of slots to be created.
        :param product: A product object which defines a set of attributes that help provide instructions on how to
                        assemble it and the elements involved in doing so.
                        The use here is to tell the belt what should go on its slots.
        """
        self.slots = [None] * belt_length
        self.belt_length = belt_length
        self.product = product
        self.unpicked_components_counter = self.generate_counter(self.product.components + ['other'])
        self.finished_products_counter = self.generate_counter(self.product.finished_product)

    @staticmethod
    def generate_counter(data: Union[List[str], str]) -> Dict[str, int]:
        local_data = data
        if isinstance(data, str):
            local_data = [data]
        elif not isinstance(data, list):
            raise ValueError(f'Dataset "{data}" must either be string or list but was "{type(data)}".')

        return {
            item: 0 for item in local_data
        }

    def move_belt(self):
        last_item = self.slots[-1]
        finished_product = self.product.finished_product

        if last_item == finished_product:
            self.finished_products_counter[last_item] += 1
        elif last_item in self.product.components:
            self.unpicked_components_counter[last_item] += 1
        else:
            self.unpicked_components_counter['other'] += 1

        self.slots = [self.product.get_item_randomly()] + self.slots[:-1]

    def remove_component(self, slot_index: int):
        self.slots[slot_index] = None


class Worker:
    next_id = 1

    def __init__(self, product: Product, assembly_time: int = 3, debug: bool = False):
        """
        An intermediate product is a combination of components apart from the final missing component
        e.g. if the components are ['A', '1', '2', 'B'] then an intermediate product is AB1, B2, A21 but not A1B2
            as that's a finished product.
        The workers can place on the belt a finished products only.
        :param product: A product object which defines a set of attributes that help provide instructions on how to
                        assemble it and the elements involved in doing so.
                        The use here is to tell the worker what needs to be assembled and how to assemble it.
        :param assembly_time: The time it takes to assemble an intermediate product or a finished product
        :param debug: Enable or disable additional console log messages
        """
        self.left_hand = None
        self.right_hand = None
        self.product = product
        self.assembly_time = assembly_time
        self.log = log.configure_logging(debug)
        self.worker_id = Worker.next_id
        Worker.next_id += 1

    def process_item(self, item: str) -> bool:
        if self.hands_occupied():
            self.assemble_component()
            # TODO if self.assembly_time > 0 invoke move_belt() here
            return False

        if (item == self.product.finished_product) or (item not in self.product.components):
            return False

        elif self.left_hand is None:
            if self.right_hand is None:
                self.left_hand = item
            elif item not in self.right_hand:
                self.left_hand = item

        elif self.right_hand is None:
            if self.left_hand is None:
                self.right_hand = item
            elif item not in self.left_hand:
                self.right_hand = item
        else:
            self.log.debug(f'Nothing for worker ({self.worker_id})')
            return False

        self.log.debug(f'Worker ({self.worker_id}) picked a component: {item}')
        self.log.debug(f'Worker ({self.worker_id}) hands: ({self.left_hand} | {self.right_hand})')
        return True

    def holds_finished_product(self) -> bool:
        if self.left_hand is None:
            return False
        return len(self.left_hand) == len(self.product.components)

    def reset_hands(self):
        self.right_hand = None
        self.left_hand = None

    def hands_occupied(self):
        return (self.left_hand is not None) and (self.right_hand is not None)

    def assemble_component(self):
        if not len(self.left_hand) < len(self.product.components):
            raise AssemblyError(f'Assembly error: inconsistent components in worker\'s hands '
                                f'({self.left_hand} | {self.right_hand})')

        self.left_hand += self.right_hand
        self.right_hand = None

        if len(self.left_hand) == len(self.product.components):
            self.log.info(
                f'Worker ({self.worker_id}) assembled a finished product: ({self.left_hand} | {self.right_hand})')
        else:
            self.log.info(
                f'Worker ({self.worker_id}) assembled intermediate product: ({self.left_hand} | {self.right_hand})')

        sleep(self.assembly_time)

    def release_finished_product(self, belt: ConveyorBelt, slot_index: int) -> ConveyorBelt:
        belt.slots[slot_index] = self.product.finished_product
        ConveyorBelt.assembled_products_combination.extend([self.left_hand])
        log.debug(f'Worker ({self.worker_id}) released a product ({self.left_hand}): {belt.slots}')
        self.reset_hands()

        return belt


def run_simulation(belt: ConveyorBelt, workers: [Worker], belt_steps: int, debug: bool = False) -> List[str]:
    """
    :param belt: A belt object
    :param workers: A list of N number of worker objects
    :param belt_steps: The number of belt iterations/steps
    :param debug: Whether to display extra debugging log messages
    :return: A list of finished product combinations
    """
    log.configure_logging(debug)

    for _ in range(belt_steps):
        belt.move_belt()
        log.debug(f'Belt: {belt.slots}')

        for i in range(belt.belt_length):
            item = belt.slots[i]
            workers_per_slot = workers[i]

            for worker in workers_per_slot:
                if item is None:
                    if worker.holds_finished_product():
                        belt = worker.release_finished_product(belt, slot_index=i)
                        break

                if item is not None:
                    picked = worker.process_item(item)
                    if not picked:
                        break

                    belt.remove_component(slot_index=i)
                    break

    assembled_products_combinations = ConveyorBelt.assembled_products_combination

    log.info(f'The products combinations: {assembled_products_combinations}')
    log.info(f'Unpicked components: {belt.unpicked_components_counter}')
    log.info(f'Finished products: {belt.finished_products_counter}')
    log.info(f'___________________________\n')

    return assembled_products_combinations


if __name__ == '__main__':
    start = timer()
    #  These configs can be passed via CLI using args parser
    _debug = False
    _belt_length = 5
    _workers_per_slot = 1
    _belt_steps = 100000
    _finished_product = 'P'
    _assembly_time = 0

    _product = Product(
        items=['A', 'B', 'C', 'D', 'E', 'F', 'AC', 'G', '1', '2', '3', '4', '5', None],
        components=['A', '2', 'C'],
        finished_product=_finished_product,
    )
    _product.validate()

    _workers = [
        [Worker(_product, _assembly_time, _debug) for _ in range(_workers_per_slot)]
        for _ in range(_belt_length)
    ]

    _belt = ConveyorBelt(_belt_length, _product)
    try:
        run_simulation(
            belt=_belt,
            workers=_workers,
            belt_steps=_belt_steps,
            debug=_debug,
        )
    except KeyboardInterrupt:
        log.info("Exiting...")

    print(f"======== Execution time: {(timer() - start):.1f} seconds ========")
    exit(SUCCESS_CODE)
