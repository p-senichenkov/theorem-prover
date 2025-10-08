from src.model.abstract.token import Token
from src.model.abstract.logical_op import LogicalOp
from src.model.concrete.and_or_not import Or, Not


class Implication(LogicalOp):
    unicode_repr = '→'
    text_repr = 'implies'

    def remove(self) -> Token:
        return Or([Not([self.operands[0]]), self.operands[1]])
