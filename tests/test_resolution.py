from unittest import TestCase

from src.model.formula_representation import *
from src.core.propositional_resolution import PropositionalResolution
from src.core.predicate_resolution import PredicateResolution
from src.core.resolution import Resolution
from src.core.skolemov_function_resolution import SkolemovFunctionResolution
from src.config.logger_conf import configure_logger
from src.util import recursively_substitute


class ResolutionTests(TestCase):

    def test_simple_resolution(self):
        formula = ImplicationSign(Variable('x'), Variable('x'))
        res = Resolution(formula)
        self.assertTrue(res.resolution())

    def test_more_complex_resolution(self):
        formula = ImplicationSign(Or([Variable('x'), Variable('y')]),
                                  Or([Variable('x'), Variable('y')]))
        res = Resolution(formula)
        self.assertTrue(res.resolution())

    def test_resolution_textbook_example_1(self):
        # P -> (Q -> R) => (P & Q) -> R
        formula = ImplicationSign(
            Implication([Variable('P'), Implication([Variable('Q'), Variable('R')])]),
            Implication([And([Variable('P'), Variable('Q')]),
                         Variable('R')]))
        res = Resolution(formula)
        self.assertTrue(res.resolution())

    def test_resolution_textbook_example_2(self):
        # John didn't meet Smith last night only if either Smith is a killer or John lies.
        # Smith isn't a killer only if John didn't met Smith last night and a murder was commited
        # after midnight.
        # If murder was commited after midnight, then either Smith is a killer or John lies.
        # Thus, Smith is a killer
        formula = ImplicationSign([
            Implication([Variable('M'), Xor([Variable('K'), Variable('L')])]),
            Implication([Not([Variable('K')]),
                         And([Variable('M'), Variable('N')])]),
            Implication([Variable('N'), Xor([Variable('K'), Variable('L')])])
        ], Variable('K'))
        res = Resolution(formula)
        self.assertFalse(res.resolution())

    def test_substitute(self):
        const_1 = SkolemovConstant()
        const_2 = SkolemovConstant()
        clause = Or([
            Not([const_1]),
            Constant('x'),
            Variable('y'),
            const_1,
            const_2,
        ])
        expected = f'(not(c_True)) or (c_\'x\') or (v_y) or (c_True) or ({repr(const_2)})'
        actual = repr(recursively_substitute(clause, Constant(True), const_1))
        self.assertEqual(actual, expected)

    def test_predicate_resolution_1(self):
        formula = ImplicationSign(Variable('x'), Forall(Variable('y'), Variable('y')))
        res = Resolution(formula)
        self.assertTrue(res.resolution())

    def test_predicate_resolution_2(self):
        formula = ImplicationSign(Or([Variable('x'), Variable('y')]),
                                  Forall(Variable('z'), Or([Variable('x'),
                                                            Variable('z')])))
        res = Resolution(formula)
        self.assertTrue(res.resolution())

    def test_predicate_textbook_example_1(self):
        '''All his ideas are brilliant. Some of his ideas are incorrect.
        Anything that is incorrect cannot be brilliant.
        Therefore, some of his ideads are delusional'''
        formula = ImplicationSign(
            And([
                Forall(
                    Variable('x'),
                    Implication([
                        CustomFunctionOrPredicate('I', [Variable('x')]),
                        CustomFunctionOrPredicate('G', [Variable('x')])
                    ])),
                Exists(
                    Variable('x'),
                    And([
                        CustomFunctionOrPredicate('I', [Variable('x')]),
                        CustomFunctionOrPredicate('W', [Variable('x')])
                    ])),
                Not([
                    Exists(
                        Variable('x'),
                        And([
                            CustomFunctionOrPredicate('W', [Variable('x')]),
                            CustomFunctionOrPredicate('G', [Variable('x')])
                        ]))
                ])
            ]),
            Exists(
                Variable('x'),
                And([
                    CustomFunctionOrPredicate('I', [Variable('x')]),
                    CustomFunctionOrPredicate('B', [Variable('x')])
                ])))

    def test_predicate_textbook_example_2(self):
        '''Every student attend lessons sometimes.
        Vasya has never attended lessons.
        Therefore, Vasya is not a student.'''
        formula = ImplicationSign(
            And([
                Forall(
                    Variable('x'),
                    Implication([
                        CustomFunctionOrPredicate('S', [Variable('x')]),
                        CustomFunctionOrPredicate('L', [Variable('x')])
                    ])),
                Not([CustomFunctionOrPredicate('L', [Constant('V')])])
            ]), Not([CustomFunctionOrPredicate('S', [Constant('V')])]))
        res = Resolution(formula)
        self.assertTrue(res.resolution())

    # def test_sk_fun_try_unify_1(self):
    #     '''Substitute f(x, y) -> x & y'''
    #     a = And([Variable('x'), Variable('y')])
    #     b = SkolemovFunction([Variable('x'), Variable('y')])
    #     expected_sk_fun = repr(b)
    #     expected_term = '(v_x) and (v_y)'
    #     answ, actual = SkolemovFunctionResolution.try_unify(a, b)
    #     self.assertTrue(answ)
    #     self.assertEqual(len(actual), 1)
    #     front = actual[0]
    #     self.assertEqual(repr(front.sk_fun), expected_sk_fun)
    #     self.assertEqual(repr(front.term), expected_term)
    #
    # def test_sk_fun_try_unify_2(self):
    #     '''Substitute f(y) -> y | z'''
    #     a = And([Variable('x'), Or([Variable('y'), Variable('z')])])
    #     sk_fun = SkolemovFunction([Variable('y')])
    #     b = And([Variable('x'), sk_fun])
    #     expected_sk_fun = repr(sk_fun)
    #     expected_term = '(v_y) or (v_z)'
    #     answ, actual = SkolemovFunctionResolution.try_unify(a, b)
    #     self.assertTrue(answ)
    #     self.assertEqual(len(actual), 1)
    #     front = actual[0]
    #     self.assertEqual(repr(front.sk_fun), expected_sk_fun)
    #     self.assertEqual(repr(front.term), expected_term)
    #
    # def test_sk_fun_try_unify_3(self):
    #     '''Substitute f(y) -> x & y, f(t, p) -> t | p'''
    #     a = Implication([And([Variable('x'), Variable('y')]), Or([Variable('t'), Variable('p')])])
    #     sk_fun_1 = SkolemovFunction([Variable('y')])
    #     sk_fun_2 = SkolemovFunction([Variable('t'), Variable('p')])
    #     b = Implication([sk_fun_1, sk_fun_2])
    #     expected_sk_fun_1 = repr(sk_fun_1)
    #     expected_term_1 = '(v_x) and (v_y)'
    #     expected_sk_fun_2 = repr(sk_fun_2)
    #     expected_term_2 = '(v_t) or (v_p)'
    #     answ, actual = SkolemovFunctionResolution.try_unify(a, b)
    #     self.assertTrue(answ)
    #     self.assertEqual(len(actual), 2)
    #     self.assertEqual(repr(actual[0].sk_fun), expected_sk_fun_1)
    #     self.assertEqual(repr(actual[0].term), expected_term_1)
    #     self.assertEqual(repr(actual[1].sk_fun), expected_sk_fun_2)
    #     self.assertEqual(repr(actual[1].term), expected_term_2)
    #
    # def test_sk_fun_try_unify_4(self):
    #     '''Variables match, but stems are different'''
    #     a = And([Variable('x'), Variable('y')])
    #     b = Or([Variable('x'), SkolemovFunction([Variable('y')])])
    #     answ, actual = SkolemovFunctionResolution.try_unify(a, b)
    #     self.assertFalse(answ)
    #     self.assertEqual(len(actual), 0)
    #
    # def test_sk_fun_try_unify_5(self):
    #     '''Stems are equal, but variables don't match'''
    #     a = And([Variable('x'), Or([Variable('y'), Variable('z')])])
    #     b = And([Variable('x'), SkolemovFunction([Variable('t'), Variable('z')])])
    #     answ, actual = SkolemovFunctionResolution.try_unify(a, b)
    #     self.assertFalse(answ)
    #     self.assertEqual(len(actual), 0)
    #
    # def test_sk_fun_try_unify_6(self):
    #     '''Substitute x | f(y) | t -> x | y | z | t'''
    #     a = Or([Variable('x'), Variable('y'), Variable('z'), Variable('t')])
    #     sk_fun = SkolemovFunction([Variable('y')])
    #     b = Or([Variable('x'), sk_fun, Variable('t')])
    #     expected_sk_fun = repr(sk_fun)
    #     expected_term = '(v_y) or (v_z)'
    #     answ, actual = SkolemovFunctionResolution.try_unify(a, b)
    #     self.assertTrue(answ)
    #     self.assertEqual(len(actual), 1)
    #     front = actual[0]
    #     self.assertEqual(repr(front.sk_fun), expected_sk_fun)
    #     self.assertEqual(repr(front.term), expected_term)
