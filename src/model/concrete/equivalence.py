from src.model.abstract.token import Token
from src.model.abstract.logical_op import LogicalOp
from src.model.concrete.and_or_not import And
from src.model.concrete.implication import Implication


class Equivalence(LogicalOp):
    unicode_repr = '↔'
    text_repr = 'equiv'

    def remove(self) -> Token:
        return And([Implication(self.operands), Implication(list(reversed(self.operands)))])
