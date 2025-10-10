from src.model.abstract.token import Token
from src.model.abstract.atom import Atom
from src.model.abstract.symbol_template import SymbolTemplate
from src.model.abstract.quantifier import Quantifier
from src.model.abstract.function_or_predicate import FunctionOrPredicate
from src.model.abstract.logical_op import LogicalOp
from src.model.abstract.nary_logical_op import NaryLogicalOp

from src.model.concrete.variable import Variable
from src.model.concrete.constant import Constant, CONSTANT_TRUE, CONSTANT_FALSE
from src.model.concrete.skolemov_constant import SkolemovConstant
from src.model.concrete.skolemov_function import SkolemovFunction
from src.model.concrete.custom_function_or_predicate import CustomFunctionOrPredicate
from src.model.concrete.implication_sign import ImplicationSign
from src.model.concrete.exists import Exists
from src.model.concrete.forall import Forall
from src.model.concrete.equals import Equals
# Not implemented yet
# from src.model.concrete.divisible_by import DivisibleBy
from src.model.concrete.and_or_not import And, Or, Not
from src.model.concrete.pierce_arrow import PierceArrow
from src.model.concrete.sheffer_stroke import ShefferStroke
from src.model.concrete.implication import Implication
from src.model.concrete.equivalence import Equivalence
from src.model.concrete.xor import Xor

# Typedefs
Clause = Or | Not | Atom | FunctionOrPredicate
