from collections.abc import Sequence

from src.model.abstract.token import Token
from src.model.concrete.variable import Variable


class Quantifier(Token):
    unicode_repr = ''
    text_repr = ''

    def __init__(self, var: Variable, body: Token):
        if not isinstance(var, Variable):
            raise TypeError(f'Variable of quantifier must be Variable, got {type(var)}')
        self.var = var
        self.body = body

    def remove(self) -> Token:
        pass

    def children(self) -> Sequence[Token]:
        return [self.body]

    def __str__(self):
        return f'{self.unicode_repr}{self.var} ({self.body})'

    def __repr__(self):
        return f'{self.text_repr} {repr(self.var)} ({repr(self.body)})'

    def replace_child(self, i: int, new_child: Token) -> Token:
        return type(self)(self.var, new_child)

    def rename_var(self, new_var: Variable) -> Token:
        return type(self)(new_var, self.body)

    def get_var(self) -> Variable:
        return self.var

    def get_body(self) -> Token:
        return self.body
