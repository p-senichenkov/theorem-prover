from typing import Any
from collections.abc import Sequence


class Token:

    def __str__(self):
        raise NotImplementedError(f'Unknown token: {type(self)}')

    def __repr__(self):
        raise NotImplementedError(f'Unknown token: {type(self)}')

    def children(self):
        return []

    def replace_child(self, num: int, new_child):
        pass

    def __eq__(self, other):
        return type(self) == type(other) and self.children() == other.children()

    def __hash__(self):
        return hash(str(self))

    # Remove all kinds of redundancy (depending on type)
    def remove_redundancy(self):
        return self


def transform_children(formula: Token, op) -> Token:
    new_children = list(map(op, formula.children()))
    for i in range(len(new_children)):
        formula = formula.replace_child(i, new_children[i])
    return formula


class Atom(Token):
    pass


class Variable(Atom):
    counter = 0

    @staticmethod
    def new_name():
        name = 'tmp' + str(Variable.counter)
        Variable.counter += 1
        return name

    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return self.name

    def __repr__(self):
        return f'v_{self.name}'

    def __eq__(self, other):
        return isinstance(other, Variable) and self.name == other.name

    __hash__ = Token.__hash__

    def get_name(self):
        return self.name


class Constant(Atom):

    def __init__(self, value: Any):
        self.value = value

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return f'c_{repr(self.value)}'

    def __eq__(self, other):
        return isinstance(other, Constant) and self.value == other.value

    __hash__ = Token.__hash__

    def get_value(self) -> Any:
        return self.value

    def is_const_true(self) -> bool:
        return self.value is True

    def is_const_false(self) -> bool:
        return self.value is False


class SymbolTemplate(Token):
    unicode_repr = ''
    text_repr = ''

    def __init__(self, args: list[Token]):
        self.args = args

    def apply_axioms(self) -> list[Token]:
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


class SkolemovConstant(Atom):
    counter = 0

    def __init__(self):
        self.name = 'c' + str(SkolemovConstant.counter)
        SkolemovConstant.counter += 1

    def __str__(self):
        return self.name

    def __repr__(self):
        return f'sc_{repr(self.name)}'

    def __eq__(self, other):
        return isinstance(other, SkolemovConstant) and self.name == other.name

    __hash__ = Token.__hash__


class SkolemovFunction(SymbolTemplate):
    counter = 0

    def __init__(self, args: list[Variable]):
        self.unicode_repr = 'f' + str(SkolemovFunction.counter)
        self.text_repr = f'sf_{self.unicode_repr}'
        SkolemovFunction.counter += 1
        self.args = args


class Quantifier(Token):
    unicode_repr = ''
    text_repr = ''

    def __init__(self, var: Variable, body: Token):
        if not isinstance(var, Variable):
            raise TypeError(f'Variable of quantifier must be Variable, got {type(var)}')
        self.var = var
        self.body = body

    def remove(self) -> Token:
        pass

    def children(self) -> list[Token]:
        return [self.body]

    def __str__(self):
        return f'{self.unicode_repr}{self.var} ({self.body})'

    def __repr__(self):
        return f'{self.text_repr} {repr(self.var)} ({repr(self.body)})'

    def replace_child(self, i: int, new_child: Token) -> Token:
        return type(self)(self.var, new_child)

    def rename_var(self, new_var: Variable) -> Token:
        return type(self)(new_var, self.body)

    def get_var(self) -> Variable:
        return self.var

    def get_body(self) -> Token:
        return self.body


class FunctionOrPredicate(SymbolTemplate):
    pass


class CustomFunctionOrPredicate(FunctionOrPredicate):
    '''Function or predicate symbol that doesn't have axioms'''

    def __init__(self, name: str, args: list[Token]):
        self.unicode_repr = name
        self.text_repr = f'cfp_{name}'
        self.args = args

    def apply_axioms(self) -> list[Token]:
        return [self]

    def replace_child(self, i: int, new_ch: Token):
        new_args = self.args[:]
        new_args[i] = new_ch
        return CustomFunctionOrPredicate(self.unicode_repr, new_args)

    def __eq__(self, other: Token) -> bool:
        return isinstance(other, CustomFunctionOrPredicate) and \
                self.unicode_repr == other.unicode_repr and self.args == other.args

    __hash__ = Token.__hash__


class LogicalOp(Token):
    unicode_repr = ''
    text_repr = ''

    def __init__(self, operands: list[Token]):
        if not isinstance(operands, Sequence):
            raise TypeError(f'Operands of LogicalOp must be a sequence (got {type(operands)})')
        self.operands = operands

    def remove(self) -> Token:
        pass

    def children(self) -> list[Token]:
        return self.operands

    def replace_child(self, i: int, new_child: Token) -> Token:
        new_ops = self.operands[:]
        new_ops[i] = new_child
        return type(self)(new_ops)

    def __str__(self):
        if len(self.operands) == 1:
            return f'{self.unicode_repr}({self.operands[0]})'
        return f' {self.unicode_repr} '.join(list(map(lambda op: f'({op})', self.operands)))

    def __repr__(self):
        if len(self.operands) == 1:
            return f'{self.text_repr}({repr(self.operands[0])})'
        return f' {self.text_repr} '.join(list(map(lambda op: f'({repr(op)})', self.operands)))


class NaryLogicalOp(LogicalOp):

    def merge(self) -> Token:
        return self


class ImplicationSign(Token):

    def __init__(self, left: Token | Sequence[Token] | None, right: Token | Sequence[Token]):
        if left is None or isinstance(left, list) and len(left) == 0:
            self.left = Constant(True)
        elif isinstance(left, Token):
            self.left = left
        else:
            self.left = And(left)

        if right is None or isinstance(right, list) and len(right) == 0:
            self.right = Constant(False)
        elif isinstance(right, Token):
            self.right = right
        else:
            self.right = And(right)

    def children(self):
        return [self.left, self.right]

    def replace_child(self, i: int, new_child: Token) -> Token:
        if i == 0:
            return ImplicationSign(new_child, self.right)
        return ImplicationSign(self.left, new_child)

    def __str__(self):
        return f'{self.left} => {self.right}'

    def __repr__(self):
        return f'{repr(self.left)} Implies {repr(self.right)}'


# Replace free occurences of var with term. Used in skolemization
def replace_free_variable(formula: Token, var: Variable, term: Token) -> Token:
    if isinstance(formula, Variable):
        if formula == var:
            return term
        return formula
    if isinstance(formula, Atom):
        return formula
    if isinstance(formula, Quantifier):
        if formula.var == var:
            # Inner occurences are bound
            return formula

    return transform_children(formula, lambda ch: replace_free_variable(ch, var, term))


""" Concrete classes """


# Concrete quantifiers
class Exists(Quantifier):
    unicode_repr = '∃'
    text_repr = 'exists'

    def remove(self, num_foralls: int) -> Token:
        if num_foralls == 0:
            return replace_free_variable(self.body, self.var, SkolemovConstant())
        # TODO: skolemov functions
        raise NotImplementedError()


class Forall(Quantifier):
    unicode_repr = '∀'
    text_repr = 'forall'

    def remove(self) -> Token:
        return self.body


# Concrete functions
# TODO


# Concrete predicates
class Equals(FunctionOrPredicate):
    unicode_repr = '='
    text_repr = 'equals'

    # TODO: how to apply axiom (a = b * c), (b = d * e) => (a = c * d * e)?

    def remove_redundancy(self):
        if self.args[0] == self.args[1]:
            return Constant(True)
        return self


class DivisibleBy(FunctionOrPredicate):
    unicode_repr = '⋮'
    text_repr = 'divby'

    def apply_axioms(self) -> list[Token]:
        # a \divby b => \exists m (a = m * b)
        m = Variable(Variable.new_name())
        return [Exists(m, Equals([self.args[0], Multiply(m, self.args[1])]))]


# Concrete logical operations
class Not(LogicalOp):
    unicode_repr = '¬'
    text_repr = 'not'

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
            if isinstance(op, Constant) and op.is_const_false():
                return Constant(False)

        # A and T <=> A
        new_ops = list(
            filter(lambda op: not isinstance(op, Constant) or not op.is_const_true(),
                   self.operands))
        if len(new_ops) < len(self.operands):
            return And(new_ops)

        # A and A <=> A
        new_ops = list(set(self.operands))
        if len(new_ops) < len(self.operands):
            return And(new_ops)

        # A and not A <=> F
        for op in self.operands:
            if not isinstance(op, Not) and Not([op]) in self.operands:
                return Constant(False)

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
            if isinstance(op, Constant) and op.is_const_true():
                return Constant(True)

        # A or F <=> A
        new_ops = list(
            filter(lambda op: not isinstance(op, Constant) or not op.is_const_false(),
                   self.operands))
        if len(new_ops) < len(self.operands):
            return Or(new_ops)

        # A or A <=> A
        new_ops = list(set(self.operands))
        if len(new_ops) < len(self.operands):
            return Or(new_ops)

        # A or not A <=> T
        for op in self.operands:
            if not isinstance(op, Not) and Not([op]) in self.operands:
                return Constant(True)

        # Single operand
        if len(self.operands) == 1:
            return self.operands[0]

        return self


class PierceArrow(LogicalOp):
    unicode_repr = '↓'
    text_repr = 'nor'

    def remove(self) -> Token:
        return Not([Or(self.operands)])


class ShefferStroke(LogicalOp):
    unicode_repr = '↑'
    text_repr = 'nand'

    def remove(self) -> Token:
        return Not([And(self.operands)])


class Implication(LogicalOp):
    unicode_repr = '→'
    text_repr = 'implies'

    def remove(self) -> Token:
        return Or([Not([self.operands[0]]), self.operands[1]])


class Equivalence(LogicalOp):
    unicode_repr = '↔'
    text_repr = 'equiv'

    def remove(self) -> Token:
        return And([Implication(self.operands), Implication(list(reversed(self.operands)))])


class Xor(LogicalOp):
    unicode_repr = '⊕'
    text_repr = 'xor'

    def remove(self) -> Token:
        return Not([Equivalence(self.operands)])
