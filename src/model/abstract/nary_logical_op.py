from src.model.abstract.token import Token
from src.model.abstract.logical_op import LogicalOp


class NaryLogicalOp(LogicalOp):

    def merge(self) -> Token:
        return self
