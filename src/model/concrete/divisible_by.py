from src.model.abstract.token import Token
from src.model.abstract.function_or_predicate import FunctionOrPredicate
from src.model.concrete.variable import Variable
from src.model.concrete.exists import Exists
from src.model.concrete.equals import Equals
from src.model.concrete.multiply import Multiply


class DivisibleBy(FunctionOrPredicate):
    unicode_repr = '⋮'
    text_repr = 'divby'
    has_axioms = True

    def apply_axioms(self) -> list[Token]:
        # a \divby b => \exists m (a = m * b)
        m = Variable(Variable.new_name())
        return [Exists(m, Equals([self.args[0], Multiply(m, self.args[1])]))]
