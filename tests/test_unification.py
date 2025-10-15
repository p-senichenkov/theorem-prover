from unittest import TestCase

from src.model.formula_representation import *
from src.core.unification import Unification
from src.core.resolution_info import UnifierInfo


class UnificationTests(TestCase):

    def unification_to_same_test(self, a: Clause, b: Clause, expected_res: bool,
                                 expected_unif: dict[Token:Token]):
        actual_res, actual_unif = Unification.try_unify_to_same(a, b)
        self.assertEqual(actual_res, expected_res)
        expected_unif = [(repr(x), repr(expected_unif[x])) for x in expected_unif]
        actual_unif = [(repr(x.source), repr(x.dest)) for x in actual_unif]
        self.assertCountEqual(actual_unif, expected_unif)

    def try_resolve_test(self, a: Clause, b: Clause, expected_res: bool,
                         expected_unif: dict[Token:Token]):
        actual_res, actual_unif = Unification.try_resolve(a, b)
        self.assertEqual(actual_res, expected_res)
        expected_unif = [(repr(x), repr(expected_unif[x])) for x in expected_unif]
        actual_unif = [(repr(x.source), repr(x.dest)) for x in actual_unif]
        self.assertCountEqual(actual_unif, expected_unif)

    def test_unify_to_same_same(self):
        self.unification_to_same_test(Implication([Variable('x'), Variable('y')]),
                                      Implication([Variable('x'), Variable('y')]), True, dict())

    def test_unify_to_same_const_var(self):
        self.unification_to_same_test(Constant('I'), Variable('x'), True,
                                      {Constant('I'): Variable('x')})

    def test_unify_to_same_const_sk_const(self):
        sk_const = SkolemovConstant()
        self.unification_to_same_test(Constant('I'), sk_const, True, {Constant('I'): sk_const})

    def test_unify_to_same_var_to_sk_const(self):
        sk_const = SkolemovConstant()
        self.unification_to_same_test(Variable('x'), sk_const, True, {Variable('x'): sk_const})

    def test_unify_to_same_sk_fun(self):
        sk_fun = SkolemovFunction([Variable('x')])
        self.unification_to_same_test(Implication([Variable('x'), Variable('y')]), sk_fun, True,
                                      {Implication([Variable('x'), Variable('y')]): sk_fun})

    def test_unify_to_same_nary(self):
        sk_fun = SkolemovFunction([Variable('b')])
        self.unification_to_same_test(
            Or([Variable('a'), Variable('b'),
                Variable('c'), Variable('d')]), Or([Variable('a'), sk_fun,
                                                    Variable('d')]), True,
            {Or([Variable('b'), Variable('c')]): sk_fun})

    def test_unify_to_same_stem_eq(self):
        sk_fun = SkolemovFunction([Variable('x')])
        self.unification_to_same_test(
            Implication([Variable('a'),
                         ShefferStroke([Variable('b'), Variable('c')])]),
            Implication([Variable('a'), sk_fun]), True,
            {ShefferStroke([Variable('b'), Variable('c')]): sk_fun})

    def test_unify_to_same_not_stem_eq(self):
        sk_fun = SkolemovFunction([Variable('x')])
        self.unification_to_same_test(
            Implication([Not([Variable('x')]),
                         Equivalence([Variable('x'), Variable('z')])]),
            Implication([Not([Variable('x')]),
                         Equivalence([Variable('x'), Not([Variable('y')])])]), False, dict())

    def test_try_resolve_negation_1(self):
        '''B is negation of A'''
        self.try_resolve_test(Variable('x'), Not([Variable('x')]), True, dict())

    def test_try_resolve_negation_2(self):
        '''A is negation of B'''
        self.try_resolve_test(Not([Variable('x')]), Variable('x'), True, dict())

    def test_try_resolve_or(self):
        '''Negation on inner level'''
        self.try_resolve_test(Or([Variable('x'), Variable('y')]),
                              Or([Variable('x'), Not([Variable('y')])]), True, dict())
