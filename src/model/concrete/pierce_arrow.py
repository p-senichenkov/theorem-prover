from src.model.abstract.token import Token
from src.model.abstract.logical_op import LogicalOp
from src.model.concrete.and_or_not import Or, Not


class PierceArrow(LogicalOp):
    unicode_repr = '↓'
    text_repr = 'nor'

    def remove(self) -> Token:
        return Not([Or(self.operands)])
