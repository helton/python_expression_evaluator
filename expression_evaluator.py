#!/usr/bin/python3
# -*- coding: utf-8 -*-


import collections
import math
import re


token_patterns = [
    ('NUMBER',      r'[0-9]*\.?[0-9]+(e[-+]?[0-9]+)?'),
    ('IDENTIFIER',  r'\w(\w|_|\d)*'),
    ('LEFT_PAREN',  r'\('),
    ('RIGHT_PAREN', r'\)'),
    ('OP_PLUS',     r'\+'),
    ('OP_MINUS',    r'\-'),
    ('OP_TIMES',    r'\*'),
    ('OP_DIVIDE',   r'/'),
    ('NEWLINE',     r'\n'),
    ('SKIP',        r'[ \t]'),
]

pattern = '|'.join('(?P<%s>%s)' % pair for pair in token_patterns)

Token = collections.namedtuple('Token', 'type value line column')


class EvalLexer(object):

    def __init__(self, expression):
        self.expression = expression

    def tokenizer(self):
        line = 1
        column = line_start = 0
        next_token = re.compile(pattern, re.IGNORECASE).match
        token = next_token(self.expression)
        while token:
            token_type = token.lastgroup
            if token_type == 'NEWLINE':
                line_start = column
                line += 1
            elif token_type != 'SKIP':
                token_value = token.group(token_type)
                yield Token(token_type, token_value, line, token.start()-line_start)
            column = token.end()
            token = next_token(self.expression, column)
        if column != len(self.expression):
            raise RuntimeError('Syntax error: Unexpected character %r on line %d' % (self.expression[column], line))


class EvalParser(object):

    def __init__(self,):
        self.stack = []
        self.variables = {"pi": math.pi, "e": math.e}

    def next_token(self):
        try:
            return next(self.tokenizer)
        except StopIteration:
            pass

    def print_tokens(self):
        line_format = "| %11s | %30s | %6s | %6s |"
        separator = '=' * 66
        print('Tokenizing...')
        print(separator)
        print(line_format % ('TYPE', 'VALUE', 'LINE', 'COLUMN'))
        print(separator)
        self.tokenizer = self.lexer.tokenizer()
        for token in self.tokenizer:
            print(line_format % token)
        print(separator)

    def evaluate(self, expression, variables=None, print_tokens=False):
        self.variables.update(variables)
        self.lexer = EvalLexer(expression)
        if print_tokens:
            self.print_tokens()
        self.tokenizer = self.lexer.tokenizer()
        self.token = self.next_token()
        self.E()
        self.result = self.stack.pop()
        return self.result

    def token_is(self, *token_types):
        if self.token:
            return self.token.type in list(token_types)

    def match(self, token_type_expected):
        if not self.token_is(token_type_expected):
            raise ValueError('Syntax error: expected %s but got %s' % (token_type_expected), self.token.type)
        else:
            self.token = self.next_token()

    def evaluate_and_push(self, token_type):
        right_value = self.stack.pop()
        left_value = self.stack.pop()
        if token_type == 'OP_PLUS':
            self.stack.append(left_value + right_value)
        elif token_type == 'OP_MINUS':
            self.stack.append(left_value - right_value)
        elif token_type == 'OP_TIMES':
            self.stack.append(left_value * right_value)
        elif token_type == 'OP_DIVIDE':
            if right_value == 0:
                raise ValueError("Semantic error: Division by zero")
            else:
                self.stack.append(left_value / right_value)

    def E(self):
        """E -> [-] T { (+|-) T }"""
        negate = self.token_is('OP_MINUS')
        if negate:
            self.match('OP_MINUS')
        self.T()
        if negate:
            self.stack.append(-float(self.stack.pop()))
        while self.token_is('OP_PLUS', 'OP_MINUS'):
            operator = self.token.type
            self.match(operator)
            self.T()
            self.evaluate_and_push(operator)

    def T(self):
        """T -> F { (*|/) F }"""
        self.F()
        while self.token_is('OP_TIMES', 'OP_DIVIDE'):
            operator = self.token.type
            self.match(operator)
            self.F()
            self.evaluate_and_push(operator)

    def F(self):
        """F -> '(' E ')' | digit | identifier"""
        if self.token_is('LEFT_PAREN'):
            self.match('LEFT_PAREN')
            self.E()
            self.match('RIGHT_PAREN')
        elif self.token_is('NUMBER'):
            self.stack.append(float(self.token.value))
            self.match('NUMBER')
        elif self.token_is('IDENTIFIER'):
            self.stack.append(float(self.variables[self.token.value]))
            self.match('IDENTIFIER')

# ------------------------ Tests --------------------------------#

status = {"OK": 0, "FAIL": 0}


def python_eval(expression, variables):
    variables.update({"pi": math.pi, "e": math.e})
    expression = ''.join(expression.split())
    if variables:
        # Need sorted by len (in reverse order) to replace variables with name is "in" other
        for key, value in sorted(variables.items(), key=lambda item: len(item[0]), reverse=True):
            expression = re.sub('\\b'+key+'\\b', str(value), expression)
    return float(eval(expression))


def test(expression, variables={}):
    """
        Test if expected value is equal to the evaluated value
    """
    parser = EvalParser()
    returned = parser.evaluate(expression, variables, True)
    expected = python_eval(expression, variables)
    if returned == expected:
        prefix = 'OK'
    else:
        prefix = 'FAIL'
    print(('# Status: %4s\n- Expression: %s\n- Returned: %f\n- Expected: %f\n- Variables: %s' %
          (prefix, expression, returned, expected, variables)))
    print('-' * 100)
    status[prefix] += 1


def run():
    print("Checking expressions...\n")
    test('123 + 987  * 230984 / (1 + 2)')
    test('8 / 3 * 2')
    test('2 + (((3 - 2)) * 7)')
    test('6 / (2 - 4 * 2) / 12 + 5 - ((0)-1)')
    test('9 * 3 / 5213 / 2134 - 29837 - (23-897 / (324+32 - (2972/9724) + 3) - 87)')
    test('1.29837643298+ 2.12332 - (2 + 2)')
    test('A + B / 2 - 9 * A + 14.23984 * B', {"A": 9, "B": 10})
    test('a12C + e * 2  - b435 / pi - 9 * e - cde + 14 * fg123', {"a12C": 19.23, "b435": 29.123, "cde": -902.12, "fg123": 82.482})
    test('92837 + 23e84 - 349.12 - (1 + 2.5)')
    test('e + 2')
    test("""1.65734 +
            3.00001 /
            4.4335 - 9.6534 * (3 - 2.12) -
            (123.111233 + 224.11 * ((32.23 / 12.342) / 234))
         """)
    print()
    count = status['OK'] + status['FAIL']
    print(("Status: OK = %.2f %%, FAIL = %.2f %%" %
          (status['OK'] * 100.00 / count, status['FAIL'] * 100.00 / count)))

if __name__ == "__main__":
    run()
