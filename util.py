from logging import getLogger

from formula_representation import Token, Quantifier

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
