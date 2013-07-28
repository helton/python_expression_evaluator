#!/usr/bin/python3
# -*- coding: utf-8 -*-

import unittest
from expression_evaluator import EvalParser

known_values = [
    ('123 + 987  * 230984 / (1 + 2)', None, 75993859.000000),
    ('8 / 3 * 2', None, 5.333333333333333),
    ('2 + (((3 - 2)) * 7)', None, 9.000000),
    ('6 / (2 - 4 * 2) / 12 + 5 - ((0)-1)', None, 5.916666666666667),
    ('9 * 3 / 5213 / 2134 - 29837 - (23-897 / (324+32 - (2972/9724) + 3) - 87)', None, -29770.49926132258),
    ('1.29837643298+ 2.12332 - (2 + 2)', None, -0.5783035670199999),
    ('A + B / 2 - 9 * A + 14.23984 * B', {"A": 9, "B": 10}, 75.39839999999998),
    ('a12C + e * 2  - b435 / pi - 9 * e - cde + 14 * fg123', {"a12C": 19.23, "b435": 29.123, "cde": -902.12, "fg123": 82.482}, 2047.7998883854561),
    ('92837 + 23e84 - 349.12 - (1 + 2.5)', None, 22999999999999998956156720947409322225359816265481975873186253670828005345271564206080.000000),
    ('e + 2', None, 4.718281828459045),
    ("""1.65734 +
            3.00001 /
            4.4335 - 9.6534 * (3 - 2.12) -
            (123.111233 + 224.11 * ((32.23 / 12.342) / 234))
    """, None, -131.77325359738896)
]


class KnownValues(unittest.TestCase):

    def test_evaluate_known_values(self):
        '''
           Check if evaluate() function in EvalParser return an
           expected value to expressions pre-defined
        '''
        parser = EvalParser()
        for expression, variables, expected in known_values:
            returned = parser.evaluate(expression, variables)
            self.assertEqual(expected, returned)

if __name__ == '__main__':
    unittest.main()
