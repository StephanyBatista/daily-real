class DomainException(Exception):
    def __init__(self, error: str) -> None:
        self._error = error

    def error(self) -> str:
        return self._error
