from collections.abc import Sequence

from src.model.abstract.token import Token
from src.model.concrete.and_or_not import And


class ImplicationSign(Token):
    '''Implication that should be proved'''

    def __init__(self, left: Token | Sequence[Token] | None, right: Token | Sequence[Token]):

        def convert_side(side: Token | Sequence[Token] | None):
            if side is None or isinstance(side, Sequence) and len(side) == 0:
                return Constant(True)
            elif isinstance(side, Token):
                return side
            elif isinstance(side, Sequence) and len(side) == 1:
                return side[0]
            else:
                return And(side)

        self.left = convert_side(left)
        self.right = convert_side(right)

    def children(self):
        return [self.left, self.right]

    def replace_child(self, i: int, new_child: Token) -> Token:
        if i == 0:
            return ImplicationSign(new_child, self.right)
        return ImplicationSign(self.left, new_child)

    def __str__(self):
        return f'{self.left!s} => {self.right!s}'

    def __repr__(self):
        return f'{self.left!r} Implies {self.right!r}'
