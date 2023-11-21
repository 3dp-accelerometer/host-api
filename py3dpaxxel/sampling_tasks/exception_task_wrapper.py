from typing import List, Callable


class ExceptionTaskWrapper(Callable):
    """
    Wrapper to store task exception that is run within its own a threading.Thread context.
    This allows the parent thread to check whether the child has raised exceptions.
    """

    def __init__(self, target: Callable[[], None]):
        self._target: Callable[[], None] = target
        self.exceptions: List[Exception] = []

    def __call__(self) -> None:
        try:
            self._target()
        except Exception as e:
            self.exceptions.append(e)
            # raise e  # the parent thread wouldn't be notified anyway
