from collections.abc import Sequence

from src.model.abstract.token import Token
from src.model.abstract.function_or_predicate import FunctionOrPredicate
from src.model.concrete.variable import Variable


class SkolemovFunction(FunctionOrPredicate):
    counter = 0

    # For testing purposes only
    @staticmethod
    def reset_counter():
        SkolemovFunction.counter = 0

    def __init__(self, args: Sequence[Variable], name: str = ""):
        assert isinstance(args, Sequence)

        if len(name) > 0:
            self.unicode_repr = name
        else:
            self.unicode_repr = 'f' + str(SkolemovFunction.counter)
            SkolemovFunction.counter += 1
        self.text_repr = f'sf_{self.unicode_repr}'
        self.args = args[:]

    def replace_child(self, i: int, new_ch: Token):
        new_args = self.args[:]
        new_args[i] = new_ch
        return SkolemovFunction(new_args, self.unicode_repr)

    def get_args(self) -> Sequence[Variable]:
        return self.args
