from collections.abc import Sequence

from src.model.abstract.token import Token
from src.model.abstract.function_or_predicate import FunctionOrPredicate


class CustomFunctionOrPredicate(FunctionOrPredicate):
    '''Function or predicate symbol that doesn't have axioms'''

    def __init__(self, name: str, args: Sequence[Token]):
        assert isinstance(args, Sequence)

        self.unicode_repr = name
        self.text_repr = f'cfp_{name}'
        self.args = args

    def apply_axioms(self) -> Sequence[Token]:
        return [self]

    def replace_child(self, i: int, new_ch: Token):
        new_args = self.args[:]
        new_args[i] = new_ch
        return CustomFunctionOrPredicate(self.unicode_repr, new_args)

    def __eq__(self, other: Token) -> bool:
        return isinstance(other, CustomFunctionOrPredicate
                          ) and self.unicode_repr == other.unicode_repr and self.args == other.args

    __hash__ = Token.__hash__

    def stem_eq(self, other) -> bool:
        return isinstance(other,
                          CustomFunctionOrPredicate) and self.unicode_repr == other.unicode_repr
