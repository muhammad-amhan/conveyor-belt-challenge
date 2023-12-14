class BaseError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class InvalidComponent(BaseError):
    def __init__(self, message: str):
        super().__init__(message)


class DuplicateComponent(BaseError):
    def __init__(self, message: str):
        super().__init__(message)


class EmptySlotRequired(BaseError):
    def __init__(self, message: str):
        super().__init__(message)


class InconsistentProduct(BaseError):
    def __init__(self, message: str):
        super().__init__(message)
