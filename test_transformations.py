from unittest import TestCase, main

from formula_representation import *
from transformations import *
from logger_conf import configure_logger

CHARS = {
        'exists': '∃',
        'forall': '∀',
        'not': '¬',
        'and': '&',
        'or': '∨',
        'pierce_arrow': '↑',
        }

class TransformationsTests(TestCase):
    def test_remove_logical_ops(self):
        formula = PierceArrow([Variable('x'), Variable('y')])
        expected = f'{CHARS['not']}((x) {CHARS['or']} (y))'
        actual = str(remove_logical_ops(formula))
        self.assertEqual(actual, expected)

    def test_narrow_negation(self):
        # TODO: all 4 cases
        formula = Not([Or([Variable('x'), Variable('y')])])
        expected = f'({CHARS['not']}(x)) {CHARS['and']} ({CHARS['not']}(y))'
        actual = str(narrow_negation(formula))
        self.assertEqual(actual, expected)

    def test_standartize_var_names(self):
        formula = Or([
            Variable('x'),
            Forall(Variable('x'), And([
                Exists(Variable('x'), Variable('y')),
                Forall(Variable('y'), Variable('x')),
                Forall(Variable('x'), Constant('x')),
                Variable('x')
                ])),
            Variable('x')
            ])
        expected = f'(x) {CHARS['or']} ({CHARS['forall']}tmp0 (({CHARS['exists']}tmp1 (y)) ' + \
                f'{CHARS['and']} ({CHARS['forall']}tmp2 (tmp0)) {CHARS['and']} ' + \
                f'({CHARS['forall']}tmp3 (x)) {CHARS['and']} (tmp0))) {CHARS['or']} (x)'
        actual = str(standartize_var_names(formula))
        self.assertEqual(actual, expected)

    def test_skolemize(self):
        # TODO: skolemov functions
        formula = Exists(Variable('x'), Or([
            Equals([Variable('x'), Variable('z')]), Exists(Variable('x'), Not([
                Equals([Variable('x'), Variable('z')])
                                                                              ]))
                                                           ]))
        expected = f'(=(c0, z)) {CHARS['or']} ({CHARS['not']}(=(c1, z)))'
        actual = str(skolemize(formula))
        self.assertEqual(actual, expected)

    def test_remove_foralls(self):
        formula = Or([Forall(Variable('x'), Forall(Variable('y'), Equals([
            Variable('x'), Variable('y')
            ]))), Variable('z')])
        expected = f'(=(x, y)) {CHARS['or']} (z)'
        actual = str(remove_foralls(formula))
        self.assertEqual(actual, expected)

    def test_to_cnf(self):
        formula = Or([
            Or([
                Variable('x'), Or([
                    Variable('y'), Constant(True), Variable('z')
                    ]), And([
                        Variable('z'), And([
                            Constant(True), Constant(False)
                            ])
                        ])
                ])
            ])
        expected = f'(x) {CHARS['or']} (y) {CHARS['or']} ({True}) {CHARS['or']} (z) ' + \
                   f'{CHARS['or']} ((z) {CHARS['and']} ({True}) {CHARS['and']} ({False}))'
        actual = str(to_cnf(formula))
        self.assertEqual(actual, expected)

    def test_break_to_clauses(self):
        formula = And([
            Equals([Variable('x'), Variable('y')]),
            And([Variable('z'), Or([Variable('t'), Variable('p')])])
            ])
        expected = ['=(x, y)', 'z', f'(t) {CHARS['or']} (p)']
        actual = list(map(str, break_to_clauses(formula)))
        self.assertEqual(actual, expected)

if __name__ == '__main__':
    configure_logger()

    main()
