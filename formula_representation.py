from typing import Any
from collections.abc import Sequence

class Token:
    def __str__(self):
        raise NotImplementedError(f'Unknown token: {type(self)}')

    def children(self):
        return []

    def replace_child(self, num: int, new_child):
        pass

    def __eq__(self, other):
        return type(self) == type(other) and self.children() == other.children()

    def __hash__(self):
        return hash(str(self))

Formula = list[Token]

class Atom(Token):
    pass

class Variable(Atom):
    counter = 0

    @staticmethod
    def new_name():
        name = 'tmp' + str(self.counter)
        self.counter += 1
        return name

    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return self.name == other.name

class Constant(Atom):
    def __init__(self, value: Any):
        self.value = value

    def __str__(self):
        return str(self.value)

    def __eq__(self, other):
        return self.value == other.value

class SymbolTemplate(Token):
    string_repr = ''

    def __init__(self, args: list[Token]):
        self.args = args

    def apply_axioms(self) -> list[Token]:
        pass

    def children(self):
        return self.args

    def replace_child(self, i: int, new_child: Token):
        self.args[i] = new_child

    def __str__(self):
        res = self.string_repr + '('
        for i in range(len(self.args)):
            if i > 0:
                res += ', '
            res += str(self.args[i])
        res += ')'
        return res

class SkolemovConstant(Atom):
    counter = 0

    def __init__(self):
        self.name = 'c' + str(SkolemovConstant.counter)
        SkolemovConstant.counter += 1

    def __str__(self):
        return self.name

class SkolemovFunction(SymbolTemplate):
    counter = 0

    def __init__(self, args: list[Variable]):
        self.string_repr = 'f' + str(SkolemovFunction.counter)
        SkolemovFunction.counter += 1
        self.args = args

class Quantifier(Token):
    string_repr = ''

    def __init__(self, var: Variable, body: Token):
        self.var = var
        self.body = body

    def remove(self) -> Token:
        pass

    def children(self) -> list[Token]:
        return [self.body]

    def __str__(self):
        return self.string_repr + str(self.var) + ' (' + str(self.body) + ')'

    def replace_child(self, i : int, new_child: Token):
        if i == 0:
            self.body = new_child
        else:
            raise IndexError(f'Index {i} is out of Quantifier\'s bounds')

class Function(SymbolTemplate):
    pass

class Predicate(SymbolTemplate):
    pass

class LogicalOp(Token):
    def __init__(self, operands: list[Token]):
        if not isinstance(operands, Sequence):
            raise TypeError(f'Operands of LogicalOp must be a sequence (got {type(operands)})')
        self.operands = operands

    def remove(self) -> Token:
        pass

    def children(self) -> list[Token]:
        return self.operands

    def replace_child(self, i: int, new_child: Token):
        self.operands[i] = new_child

class BinaryLogicalOp(LogicalOp):
    string_repr = ''

    def __str__(self):
        return '(' + str(self.operands[0]) + ') ' + self.string_repr + \
               ' (' + str(self.operands[1]) + ')'

class NaryLogicalOp(LogicalOp):
    string_repr = ''

    def __str__(self):
        return '(' + f' {self.string_repr} '.join(map(str, self.operands)) + ')'

class ImplicationSign(Token):
    def __init__(self, left: Token, right: Token):
        self.left = left
        self.right = right

    def children(self):
        return [self.left, self.right]

    def replace_child(self, i: int, new_child: Token):
        if i == 0:
            self.left = new_child
        else:
            self.right = new_child

    def __str__(self):
        return str(self.left) + ' => ' + str(self.right)

# Replace free occurences of var with term. Used in skolemization
def replace_free_variable(formula: Token, var: Variable, term: Token) -> Token:
    if isinstance(formula, Variable):
        if formula == var:
            return term
    if isinstance(formula, Atom):
        return formula
    if isinstance(formula, Quantifier):
        if formula.var == var:
            # Inner occurences are bound
            return formula

    children = formula.children()
    for i in range(len(children)):
        child = children[i]
        formula.replace_child(i, replace_free_variable(child, var, term))
    return formula

""" Concrete classes """
# Concrete quantifiers
class Exists(Quantifier):
    string_repr = '∃'

    def remove(self, num_foralls: int) -> Formula:
        if num_foralls == 0:
            return replace_free_variable(self.body, self.var, SkolemovConstant())
        # TODO: skolemov functions
        raise NotImplementedError()

class Forall(Quantifier):
    string_repr = '∀'

    def remove(self) -> Formula:
        return self.body

# Concrete functions
class Multiply(Function):
    pass

# Concrete predicates
class Equals(Predicate):
    string_repr = '='
    # TODO: how to apply axiom (a = b * c), (b = d * e) => (a = c * d * e)?

class DivisibleBy(Predicate):
    def apply_axioms(self) -> list[Token]:
        # a \divby b => \exists m (a = m * b)
        m = Variable(Variable.new_name())
        return [Exists(m, Equals([self.args[0], Multiply(m, self.args[1])]))]

# Concrete logical operations
class Not(LogicalOp):
    def __str__(self):
        return '¬(' + str(self.operands[0]) + ')'

    def narrow(self) -> Token:
        operand = self.operands[0]
        # Quantifier rules
        if isinstance(operand, Forall):
            return Exists(operand.var, Not([operand.body]))
        if isinstance(operand, Exists):
            return Forall(operand.var, Not([operand.body]))
        # De Morgan's laws
        if isinstance(operand, And):
            return Or(list(map(lambda ch: Not([ch]), operand.children())))
        if isinstance(operand, Or):
            return And(list(map(lambda ch: Not([ch]), operand.children())))
        return self

    def children(self):
        return self.operands

    def replace_child(self, i: int, new_child: Token):
        self.operands[0] = new_child

class And(NaryLogicalOp):
    string_repr = '&'

class Or(NaryLogicalOp):
    string_repr = '∨'

class PierceArrow(BinaryLogicalOp):
    string_repr = '↑'

    def remove(self) -> Token:
        return Not([Or(self.operands)])

class Implication(BinaryLogicalOp):
    string_repr = '→'

    def remove(self) -> Token:
        return Or([Not([self.operands[0]]), self.operands[1]])
