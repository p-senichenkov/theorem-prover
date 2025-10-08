from logging import getLogger

from src.model.formula_representation import *
from src.util import transform_children, replace_free_variable

logger = getLogger(__name__)


# 1. Remove all logical operations, except for And, Or, Not
def remove_logical_ops(formula: Token) -> Token:
    if isinstance(formula, LogicalOp) and not isinstance(formula, And | Or | Not):
        formula = formula.remove()
        return remove_logical_ops(formula)

    return transform_children(formula, remove_logical_ops)


# 2. Narrow negation operations as much as possible
def narrow_negation(formula: Token) -> Token:
    while isinstance(formula, Not):
        new_formula = formula.narrow()
        if new_formula == formula:
            break
        formula = new_formula

    return transform_children(formula, narrow_negation)


# 3. Standartize variable names ("alpha-conversion")
def standartize_var_names(formula: Token, known_names: set[str] = set()) -> Token:
    if isinstance(formula, Quantifier):
        old_name = formula.var.get_name()
        logger.debug(f'Formula: {formula}')
        logger.debug(f'Variable name: {old_name}, known names: {list(map(str, known_names))}')
        if old_name in known_names:
            new_name = old_name
            while new_name in known_names:
                new_name = Variable.new_name()
            new_var = Variable(new_name)
            new_body = replace_free_variable(formula.body, formula.var, new_var)
            formula = formula.rename_var(new_var)
            formula = formula.replace_child(0, new_body)
            logger.debug(f'After replacing free variables: {formula}')
            known_names.add(new_name)
        else:
            known_names.add(old_name)
    elif isinstance(formula, Variable):
        known_names.add(formula.get_name())

    return transform_children(formula, lambda c: standartize_var_names(c, known_names))


# 4. Get rid of existance quantifier ("skolemize")
def skolemize(formula: Token, universal_variables: list[Variable] = []) -> Token:
    if isinstance(formula, Exists):
        formula = formula.remove(universal_variables)
        return skolemize(formula, universal_variables)
    elif isinstance(formula, Forall):
        universal_variables.append(formula.get_var())

    children = formula.children()
    for i in range(len(children)):
        child = children[i]
        formula = formula.replace_child(i, skolemize(child, universal_variables))
    return formula


# 5, 6. Move universal quantifiers to the beginning and remove them
def remove_foralls(formula: Token) -> Token:
    if isinstance(formula, Forall):
        formula = formula.body
        return remove_foralls(formula)

    children = formula.children()
    for i in range(len(children)):
        child = children[i]
        formula = formula.replace_child(i, remove_foralls(child))
    return formula


# 7. Conjunctive normal form:
#   a. Merge n-ary logical operations
def merge_nary_ops(formula: Token) -> Token:
    while isinstance(formula, NaryLogicalOp):
        new_formula = formula.merge()
        if new_formula == formula:
            break
        formula = new_formula

    children = formula.children()
    for i in range(len(children)):
        child = children[i]
        formula = formula.replace_child(i, to_cnf(child))
    return formula


#   b. Apply Or's distributivity
def distribute(formula: Token) -> Token:
    if isinstance(formula, Or):
        formula = formula.distribute()

    children = formula.children()
    for i in range(len(children)):
        child = children[i]
        formula = formula.replace_child(i, distribute(child))
    return formula


def to_cnf(formula: Token) -> Token:
    while True:
        new_formula = merge_nary_ops(formula)
        new_formula = distribute(new_formula)
        if new_formula == formula:
            return new_formula
        formula = new_formula


# 7.5. Remove all kinds of redundancies
def remove_redundancy_rec(formula: Token) -> Token:
    while True:
        new_formula = formula.remove_redundancy()
        if new_formula == formula:
            break
        formula = new_formula

    children = formula.children()
    for i in range(len(children)):
        child = children[i]
        formula = formula.replace_child(i, remove_redundancy_rec(child))
    return formula


def remove_redundancy(formula: Token) -> Token:
    while True:
        logger.debug(f'\tFormula: {formula}')
        new_formula = remove_redundancy_rec(formula)
        logger.debug(f'\t\tNew formula: {new_formula}')
        if new_formula == formula:
            logger.debug('\t\tEqual')
            return formula
        formula = new_formula


# 8. Break to clauses (assume that conjunctions are outermost)
def break_to_clauses(formula: Token) -> list[Token]:
    if isinstance(formula, And):
        formulas = formula.children()
        clauses = []
        for form in formulas:
            clauses += break_to_clauses(form)
        return clauses
    return [formula]
