from collections.abc import Sequence

from src.model.abstract.token import Token


class SymbolTemplate(Token):
    unicode_repr = ''
    text_repr = ''

    def __init__(self, args: Sequence[Token]):
        self.args = args

    def apply_axioms(self) -> Sequence[Token]:
        pass

    def children(self):
        return self.args

    def replace_child(self, i: int, new_child: Token) -> Token:
        new_args = self.args[:]
        new_args[i] = new_child
        return type(self)(new_args)

    def __str__(self):
        return f'{self.unicode_repr}({', '.join(list(map(str, self.args)))})'

    def __repr__(self):
        return f'{self.text_repr}({', '.join(list(map(repr, self.args)))})'
