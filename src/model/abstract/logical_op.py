from collections.abc import Sequence

from src.model.abstract.token import Token


class LogicalOp(Token):
    unicode_repr = ''
    text_repr = ''

    def __init__(self, operands: Sequence[Token]):
        assert isinstance(operands, Sequence)

        self.operands = operands

    def remove(self) -> Token:
        pass

    def children(self) -> Sequence[Token]:
        return self.operands

    def replace_child(self, i: int, new_child: Token) -> Token:
        new_ops = self.operands[:]
        new_ops[i] = new_child
        return type(self)(new_ops)

    def __str__(self):
        if len(self.operands) == 1:
            return f'{self.unicode_repr}({self.operands[0]!s})'
        return f' {self.unicode_repr} '.join(list(map(lambda op: f'({op!s})', self.operands)))

    def __repr__(self):
        if len(self.operands) == 1:
            return f'{self.text_repr}({self.operands[0]!r})'
        return f' {self.text_repr} '.join(list(map(lambda op: f'({op!r})', self.operands)))
