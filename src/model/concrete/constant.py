from typing import Any

from src.model.abstract.token import Token
from src.model.abstract.atom import Atom


class Constant(Atom):

    def __init__(self, value: Any):
        self.value = value

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return f'c_{repr(self.value)}'

    def __eq__(self, other):
        return isinstance(other, Constant) and self.value == other.value

    __hash__ = Token.__hash__

    def get_value(self) -> Any:
        return self.value


CONSTANT_TRUE = Constant(True)
CONSTANT_FALSE = Constant(False)
