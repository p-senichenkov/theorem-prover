from src.model.abstract.token import Token
from src.model.abstract.logical_op import LogicalOp
from src.model.concrete.and_or_not import And, Not


class ShefferStroke(LogicalOp):
    unicode_repr = '↑'
    text_repr = 'nand'

    def remove(self) -> Token:
        return Not([And(self.operands)])
