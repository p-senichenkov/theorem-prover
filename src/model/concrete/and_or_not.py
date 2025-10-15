from src.model.abstract.token import Token
from src.model.abstract.logical_op import LogicalOp
from src.model.abstract.nary_logical_op import NaryLogicalOp
from src.model.concrete.exists import Exists
from src.model.concrete.forall import Forall
from src.model.concrete.constant import Constant, CONSTANT_TRUE, CONSTANT_FALSE
'''These oeprations should be in one file because of curcular dependency'''


class And(NaryLogicalOp):
    unicode_repr = '&'
    text_repr = 'and'

    def merge(self) -> Token:
        new_operands = []

        for i in range(len(self.operands)):
            op = self.operands[i]
            if isinstance(op, And):
                new_operands += op.operands
            else:
                new_operands.append(op)
        return And(new_operands)

    def remove_redundancy(self) -> Token:
        # A and F <=> F
        for op in self.operands:
            if isinstance(op, Constant) and op == CONSTANT_FALSE:
                return CONSTANT_FALSE

        # A and T <=> A
        new_ops = list(
            filter(lambda op: not isinstance(op, Constant) or op != CONSTANT_TRUE, self.operands))
        if len(new_ops) < len(self.operands):
            return And(new_ops)

        # A and A <=> A
        new_ops = list(set(self.operands))
        if len(new_ops) < len(self.operands):
            return And(new_ops)

        # A and not A <=> F
        for op in self.operands:
            if not isinstance(op, Not) and Not([op]) in self.operands:
                return CONSTANT_FALSE

        # Single operand
        if len(self.operands) == 1:
            return self.operands[0]

        return self


class Or(NaryLogicalOp):
    unicode_repr = '∨'
    text_repr = 'or'

    def merge(self) -> Token:
        new_operands = []

        for i in range(len(self.operands)):
            op = self.operands[i]
            if isinstance(op, Or):
                new_operands += op.operands
            else:
                new_operands.append(op)
        return Or(new_operands)

    # Apply distributive law to *first* And child
    def distribute(self) -> Token:
        for i in range(len(self.operands)):
            op = self.operands[i]
            if isinstance(op, And):
                new_ops = []
                for and_op in op.children():
                    new_or_ops = self.operands[:]
                    new_or_ops[i] = and_op
                    new_ops.append(Or(new_or_ops))
                return And(new_ops)
        return self

    def remove_redundancy(self) -> Token:
        # A or T <=> T
        for op in self.operands:
            if isinstance(op, Constant) and op == CONSTANT_TRUE:
                return CONSTANT_TRUE

        # A or F <=> A
        new_ops = list(
            filter(lambda op: not isinstance(op, Constant) or op != CONSTANT_FALSE, self.operands))
        if len(new_ops) < len(self.operands):
            return Or(new_ops)

        # A or A <=> A
        new_ops = list(set(self.operands))
        if len(new_ops) < len(self.operands):
            return Or(new_ops)

        # A or not A <=> T
        for op in self.operands:
            if not isinstance(op, Not) and Not([op]) in self.operands:
                return CONSTANT_TRUE

        # Single operand
        if len(self.operands) == 1:
            return self.operands[0]

        return self


class Not(LogicalOp):
    unicode_repr = '¬'
    text_repr = 'not'
    operands_num = 1

    def narrow(self) -> Token:
        operand = self.operands[0]
        # Quantifier rules
        if isinstance(operand, Forall):
            return Exists(operand.get_var(), Not([operand.get_body()]))
        if isinstance(operand, Exists):
            return Forall(operand.get_var(), Not([operand.get_body()]))
        # De Morgan's laws
        if isinstance(operand, And):
            return Or(list(map(lambda ch: Not([ch]), operand.children())))
        if isinstance(operand, Or):
            return And(list(map(lambda ch: Not([ch]), operand.children())))
        # Double negation
        if isinstance(operand, Not):
            return operand.children()[0]
        return self
