from collections.abc import Sequence
from logging import getLogger

from src.model.abstract.token import Token
from src.model.abstract.quantifier import Quantifier
from src.model.concrete.variable import Variable
from src.model.concrete.skolemov_constant import SkolemovConstant
from src.model.concrete.skolemov_function import SkolemovFunction
from src.util import replace_free_variable

logger = getLogger(__name__)


class Exists(Quantifier):
    unicode_repr = '∃'
    text_repr = 'exists'

    def remove(self, variables: Sequence[Variable] = []) -> Token:
        if len(variables) == 0:
            return replace_free_variable(self.body, self.var, SkolemovConstant())
        sk_fun = SkolemovFunction(variables)
        logger.debug(f'Created Skolemov fucntion: {sk_fun}')
        return replace_free_variable(self.body, self.var, sk_fun)
