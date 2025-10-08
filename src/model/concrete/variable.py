from src.model.abstract.token import Token
from src.model.abstract.atom import Atom


class Variable(Atom):
    counter = 0

    # For testing purposes only
    @staticmethod
    def reset_counter():
        print('\tCounter reset.')
        Variable.counter = 0

    @staticmethod
    def new_name():
        print(f'Creating new name: tmp{Variable.counter}')
        name = 'tmp' + str(Variable.counter)
        Variable.counter += 1
        return name

    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return self.name

    def __repr__(self):
        return f'v_{self.name}'

    def __eq__(self, other):
        return isinstance(other, Variable) and self.name == other.name

    __hash__ = Token.__hash__

    def get_name(self):
        return self.name
