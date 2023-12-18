from main import ConveyorBelt, Worker, Product


class Factory:
    def __init__(
            self,
            belt_length=3,
            belt_iterations=100,
            finished_product='P',
            assembly_time=0,
            workers_per_slot=1,
            belt_delay=0,
            debug=False,
    ):
        self.belt_length = belt_length
        self.belt_iterations = belt_iterations
        self.belt_delay = belt_delay
        self.finished_product = finished_product
        self.assembly_time = assembly_time
        self.workers_per_slot = workers_per_slot
        self.debug = debug

        self.product = Product(
            items=['A', 'B', 'C', 'D', 'E', 'F', None],
            components=['A', 'B', 'C'],
            finished_product=self.finished_product,
        )
        self.belt = ConveyorBelt(self.belt_length, self.product, self.belt_iterations, self.belt_delay)

        self.workers = [
            [Worker(self.belt, self.product) for _ in range(self.workers_per_slot)]
            for _ in range(self.belt_length)
        ]
