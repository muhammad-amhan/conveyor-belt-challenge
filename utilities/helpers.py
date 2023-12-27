import json
from typing import Dict

from utilities.constants import ERROR_CODE
from utilities.logger import Logger

log = Logger(__name__)


class JSONFileHandler:
    def __init__(self):
        pass

    @staticmethod
    def read_json(filename) -> Dict[any, any]:
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            log.error(f'File "{filename}" not found.')
            exit(ERROR_CODE)
        except json.JSONDecodeError as e:
            log.error(f'Error decoding JSON file "{filename}": {e}')
            exit(ERROR_CODE)

