from src.model.abstract.token import Token
from src.model.abstract.function_or_predicate import FunctionOrPredicate
from src.model.concrete.constant import Constant, CONSTANT_TRUE, CONSTANT_FALSE


class IsTrue(FunctionOrPredicate):
    '''Function S(x) = x for propositional variables'''
    unicode_repr = 'IsTrue'
    text_repr = 'p_IsTrue'
    num_args = 1
    has_axioms = True

    def apply_axioms(self, entire_formula: Token) -> list[Token]:
        if self.args[0] == CONSTANT_TRUE:
            return [CONSTANT_TRUE]
        if self.args[0] == CONSTANT_FALSE:
            return [CONSTANT_FALSE]
        return []
