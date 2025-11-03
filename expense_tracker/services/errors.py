class GroupNotFound(Exception):
    """Raised when a group id does not exist in the data store."""
    pass


class ExpenseNotFound(Exception):
    """Raised when an expense id does not exist in the data store."""
    pass


class SplitValidationError(Exception):
    """
    Raised when provided split information is invalid
    (e.g., no users for equal split, shares sum <= 0, percent sum != 100).
    """
    def __init__(self, message: str, code: str = "invalid_split"):
        super().__init__(message)
        self.code = code
