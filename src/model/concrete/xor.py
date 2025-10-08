from src.model.abstract.token import Token
from src.model.abstract.logical_op import LogicalOp
from src.model.concrete.and_or_not import Not
from src.model.concrete.equivalence import Equivalence


class Xor(LogicalOp):
    unicode_repr = '⊕'
    text_repr = 'xor'

    def remove(self) -> Token:
        return Not([Equivalence(self.operands)])
