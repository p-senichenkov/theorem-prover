from logging import getLogger

from src.model.abstract.token import Token
from src.model.abstract.atom import Atom
from src.model.abstract.quantifier import Quantifier
from src.model.concrete.variable import Variable

logger = getLogger(__name__)


def recursive_search(formula: Token, pred) -> bool:
    if pred(formula):
        return True
    for ch in formula.children():
        if recursive_search(ch, pred):
            return True
    return False


def recursive_filter(formula: Token, pred) -> list[Token]:
    if pred(formula):
        return [formula]
    result = []
    for ch in formula.children():
        result += recursive_filter(ch, pred)
    return result


def recursive_instances(formula: Token, type_) -> list[Token]:
    return recursive_filter(formula, lambda f: isinstance(f, type_))


def recursively_transform_children(formula: Token, op) -> Token:
    formula = op(formula)

    new_children = list(map(lambda f: recursively_transform_children(f, op), formula.children()))
    for i in range(len(new_children)):
        formula = formula.replace_child(i, new_children[i])
    return formula


def transform_children(formula: Token, op) -> Token:
    new_children = list(map(op, formula.children()))
    for i in range(len(new_children)):
        formula = formula.replace_child(i, new_children[i])
    return formula


# Replace free occurences of var with term. Used in skolemization
def replace_free_variable(formula: Token, var: Variable, term: Token) -> Token:
    logger.debug(f'Replacing free occurences of {var} with {term} in {formula}...')
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


def recursively_substitute(formula: Token, source: Token, dest: Token) -> Token:
    '''Substitute source instead of all occurences of dest in formula'''
    return recursively_transform_children(formula, lambda x: source if x == dest else x)
