from src.model.abstract.function_or_predicate import FunctionOrPredicate
from src.model.concrete.constant import Constant


class Equals(FunctionOrPredicate):
    unicode_repr = '='
    text_repr = 'equals'

    # TODO: how to apply axiom (a = b * c), (b = d * e) => (a = c * d * e)?

    def remove_redundancy(self):
        if self.args[0] == self.args[1]:
            return Constant(True)
        return self
