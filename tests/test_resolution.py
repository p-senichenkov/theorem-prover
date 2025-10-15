from unittest import TestCase

from src.model.formula_representation import *
from src.core.resolution import Resolution
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
        '''x | y => forall z (x & z)'''
        formula = ImplicationSign(Or([Variable('x'), Variable('y')]),
                                  Forall(Variable('z'), And([Variable('x'),
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

    def test_sk_fun_resolution_1(self):
        '''forall x (exists y (x & y)) => Pred(x -> y) | x'''
        formula = ImplicationSign(
            Forall(Variable('x'), Exists(Variable('y'), And([Variable('x'),
                                                             Variable('y')]))),
            Or([
                CustomFunctionOrPredicate('Pred',
                                          [Implication([Variable('x'), Variable('y')])]),
                Variable('x')
            ]))
        res = Resolution(formula)
        self.assertTrue(res.resolution())
