from src.model.abstract.token import Token
from src.model.abstract.atom import Atom


class SkolemovConstant(Atom):
    counter = 0

    # For testing purposes only
    @staticmethod
    def reset_counter():
        SkolemovConstant.counter = 0

    def __init__(self):
        self.name = 'c' + str(SkolemovConstant.counter)
        SkolemovConstant.counter += 1

    def __str__(self):
        return self.name

    def __repr__(self):
        return f'sc_{repr(self.name)}'

    def __eq__(self, other):
        return isinstance(other, SkolemovConstant) and self.name == other.name

    __hash__ = Token.__hash__
