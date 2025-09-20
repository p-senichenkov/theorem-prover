from formula_representation import *

# 1. Remove all logical operations, except for And, Or, Not
def remove_logical_ops(formula: Token) -> Token:
    if isinstance(formula, LogicalOp) and not isinstance(formula, And | Or | Not):
        formula = formula.remove()
        return remove_logical_ops(formula)

    children = formula.children()
    for i in range(len(children)):
        child = children[i]
        formula.replace_child(i, remove_logical_ops(child))
    return formula

# 2. Narrow negation operations as much as possible
def narrow_negation(formula: Token) -> Token:
    while isinstance(formula, Not):
        new_formula = formula.narrow()
        if new_formula == formula:
            break
        formula = new_formula

    children = formula.children()
    for i in range(len(children)):
        child = children[i]
        formula.replace_child(i, narrow_negation(child))
    return formula

# 3. Standartize variable names ("alpha-conversion") -- skip for now
# TODO: "alpha-conversion"

# 4. Get rid of existance quantifier ("skolemize")
def skolemize(formula: Token, num_foralls: int = 0) -> Token:
    if isinstance(formula, Exists):
        formula = formula.remove(num_foralls)
        return skolemize(formula)
    elif isinstance(formula, Forall):
        num_foralls += 1

    children = formula.children()
    for i in range(len(children)):
        child = children[i]
        formula.replace_child(i, skolemize(child, num_foralls))
    return formula

# 5, 6. Move universal quantifiers to the beginning and remove them
def remove_foralls(formula: Token) -> Token:
    if isinstance(formula, Forall):
        formula = formula.body
        return remove_foralls(formula)

    children = formula.children()
    for i in range(len(children)):
        child = children[i]
        formula.replace_child(i, remove_foralls(child))
    return formula

# 7. Conjunctive normal form
# Currently it's just merging of Ors and Ands with their children
def to_cnf(formula: Token) -> Token:
    while isinstance(formula, Or) or isinstance(formula, And):
        new_formula = formula.merge()
        if new_formula == formula:
            break
        formula = new_formula

    children = formula.children()
    for i in range(len(children)):
        child = children[i]
        formula.replace_child(i, to_cnf(child))
    return formula

# 8. Break to clauses (assume that conjunctions are outermost)
def break_to_clauses(formula: Token) -> list[Token]:
    if isinstance(formula, And):
        formulas = formula.children()
        clauses = []
        for form in formulas:
            clauses += break_to_clauses(form)
        return clauses
    return [formula]
