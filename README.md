# Conveyor Belt Coding Challenge

## Exercise Details
Please check the challenge question details [here](exercise/exercise.txt).

## Requirements
- `Python >= 3.10` due to the use of `|` for type checks using typings
```bash
> git clone https://github.com/your_username/your_project.git
> cd conveyor-belt
> pip3 install -r requirements.txt
```

## Run the Simulation
- Modify the JSON [config](config/config.json)
```bash 
> python3 main.py
```

## Run Tests
Tests are under [tests/](tests):
```bash
> pytest tests/
```

## Assumptions
Some personal assumptions were needed to fill-in gaps and make sense of the task. Here are some:
* Items can come into the belt at random intervals.
* Each slot can hold one item or a finished product (e.g. "P" - bound to user input).
* Each slot can have a dynamic number of workers.
* Every N seconds, the belt moves one position.
* Each worker can either pick a component or place a finished product onto the slot (one worker operates on each slot).
* It takes N seconds to assemble an intermediate product or a final product.
    - If set, it means some components might pass without being picked up by any worker.
* During the N-second assembly time, workers can't interact with the belt.
    - Workers can remain holding any two of (component, intermediate product, or a finished product) at a time in each hand e.g. (BC, A) (None, C) (None, A) (ABC, None) or (ABC, B).
* There should be an equal chance of any items to enter the belt.
* If a worker constructed an intermediate product, look only for the missing final component.
* The intermediate product is always assembled and placed in the worker's left hand.
   - Example:
       ```
       ('A', 'B') -> ('AB', None) -> found C -> pick C -> ('AB', 'C') -> ('ABC', None)
       ```
   - `<finished_product>` will be placed on the belt.
   - When a final component is found, it should be picked by the right hand, then assembled in the left hand as presented above.
