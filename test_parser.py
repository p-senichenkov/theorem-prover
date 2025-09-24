from unittest import TestCase, main

from parser import parser

class ParserTests(TestCase):
    def templated_test(self, formula: str, expected: str):
        result = parser.parse(formula)
        self.assertEqual(repr(result), expected)

    def test_constant(self):
        self.templated_test('\'0.5\' => \'17\'', 'c_0.5 Implies c_17')

    def test_variable(self):
        self.templated_test('x => y', 'v_x Implies v_y')

    def test_or(self):
        self.templated_test('(x) or (y) or (z) => (t)', '((v_x) or (v_y)) or (v_z) Implies v_t')

    def test_and(self):
        self.templated_test('(x) and (y) and (z) => (t)', '((v_x) and (v_y)) and (v_z) Implies v_t')

    def test_divby(self):
        self.templated_test('divby(x, y) => z', 'divby(v_x, v_y) Implies v_z')

    def test_equals(self):
        self.templated_test('=(x, y) => z', 'equals(v_x, v_y) Implies v_z')

    def test_not(self):
        self.templated_test('not(x) => z', 'not(v_x) Implies v_z')

    def test_forall(self):
        self.templated_test('forall x (y) => z', 'forall v_x (v_y) Implies v_z')

    def test_exists(self):
        self.templated_test('exists x (y) => z', 'exists v_x (v_y) Implies v_z')

if __name__ == '__main__':
    main()
