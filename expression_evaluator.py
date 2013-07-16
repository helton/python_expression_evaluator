import math


class Token:

    # Start in 1 because 0 is a boolean value evaluated to False
    (ID, NUMBER, PLUS, MINUS, TIMES, DIVIDE, LEFT_PAREN, RIGHT_PAREN) = range(1, 9)

    dict_token_type = {
        ID: "identifier",
        NUMBER: "number",
        PLUS: "'+'",
        MINUS: "'-'",
        TIMES: "'*'",
        DIVIDE: "'/'",
        LEFT_PAREN: "'('",
        RIGHT_PAREN: "')'"
    }

    @classmethod
    def token_type_to_string(self, *token_types):
        return ', '.join([self.dict_token_type[tt] for tt in token_types])

    def __init__(self, token_type, lexeme, lexeme_value=None):
        self.token_type = token_type
        self.lexeme = lexeme
        self.lexeme_value = lexeme_value

    def __repr__(self):
        return ("Token type: %8s | Lexeme = %s | Lexeme value = %s" %
                (str(self.token_type_to_string(self.token_type)), self.lexeme, str(self.lexeme_value)))


class Lexer:

    tokens = []
    index = 0
    symbols = '+-*/()'

    def __init__(self, expression):
        self.expression = ''.join(expression.split())

    def clear(self):
        self.tokens = []
        self.index = 0

    def finished(self):
        return self.index >= len(self.expression)

    def get_char(self):
        if not self.finished():
            self.index += 1
            return self.expression[self.index - 1]
        return None

    def peek(self):
        if not self.finished():
            return self.expression[self.index]

    def skip_spaces(self):
        while not self.finished() and self.expression[self.index].isspace():
            self.index += 1

    def read_number(self):
        lexeme = ""
        while not self.finished():
            c = self.peek()
            if (lexeme + c).isnumeric():
                lexeme += self.get_char()
            else:
                break
        if lexeme:
            return Token(Token.NUMBER, lexeme, float(lexeme))

    def read_symbol(self):
        if not self.finished() and self.peek() in self.symbols:
            lexeme = self.get_char()
            if lexeme == '+':
                return Token(Token.PLUS, lexeme)
            elif lexeme == '-':
                return Token(Token.MINUS, lexeme)
            elif lexeme == '*':
                return Token(Token.TIMES, lexeme)
            elif lexeme == '/':
                return Token(Token.DIVIDE, lexeme)
            elif lexeme == '(':
                return Token(Token.LEFT_PAREN, lexeme)
            elif lexeme == ')':
                return Token(Token.RIGHT_PAREN, lexeme)

    def read_identifier(self):
        lexeme = ""
        while not self.finished():
            c = self.peek()
            if (lexeme + c).isidentifier():
                lexeme += self.get_char()
            else:
                break
        if lexeme:
            return Token(Token.ID, lexeme, lexeme)

    def tokenize(self):
        self.clear()
        while not self.finished():
            self.skip_spaces()
            token = self.read_number()
            if token:
                self.tokens.append(token)
            token = self.read_symbol()
            if token:
                self.tokens.append(token)
            token = self.read_identifier()
            if token:
                self.tokens.append(token)
        return self.tokens


class Parser:
    """
        Parse the expression as input

        Grammar in EBNF [Extended Backus-Naur Form]:
        E -> [-] T { (+|-) T }
        T -> F { (*|/) F }
        F -> '(' E ')' | digit | identifier
    """

    variables = {}
    tokens = []
    stack = []
    result = 0.0
    token = None
    index = 0

    def clear(self):
        self.result = 0.0
        self.index = 0
        self.token = None
        self.stack = []
        self.tokens = []
        self.variables = {"pi": math.pi, "e": math.e}

    def evaluate(self, expression, variables={}):
        self.clear()
        self.expression = ''.join(expression.split())
        self.variables.update(variables)
        self.lexer = Lexer(expression)
        self.tokens = self.lexer.tokenize()
        self.token = self.next_token()
        self.E()
        self.result = self.stack.pop()
        return self.result

    def print_tokens(self):
        for token in self.tokens:
            print(token)

    def token_is(self, *token_types):
        if not self.token:
            raise ValueError('Syntax error: Unexpected end of expression.')
        return self.token.token_type in list(token_types)

    def finished(self):
        return self.index >= len(self.tokens)

    def next_token(self):
        if not self.finished():
            self.index += 1
            return self.tokens[self.index - 1]

    def match(self, token_type_expected):
        if not self.token_is(token_type_expected):
            raise ValueError('Syntax error: expected %s but got %s' % (Token.token_type_to_string(token_type_expected), Token.token_type_to_string(self.token.token_type)))
        else:
            self.token = self.next_token()

    def evaluate_and_push(self, token_type):
        right_value = self.stack.pop()
        left_value = self.stack.pop()
        if token_type == Token.PLUS:
            self.stack.append(left_value + right_value)
        elif token_type == Token.MINUS:
            self.stack.append(left_value - right_value)
        elif token_type == Token.TIMES:
            self.stack.append(left_value * right_value)
        elif token_type == Token.DIVIDE:
            if right_value == 0:
                raise ValueError("Semantic error: Division by zero")
            else:
                self.stack.append(left_value / right_value)

    def E(self):
        """E -> [-] T { (+|-) T }"""
        negate = self.token_is(Token.MINUS)
        if negate:
            self.match(Token.MINUS)
        self.T()
        if negate:
            self.stack.append(-self.stack.pop())
        while not self.finished() and self.token_is(Token.PLUS, Token.MINUS):
            operator = self.token.token_type
            self.match(operator)
            self.T()
            self.evaluate_and_push(operator)

    def T(self):
        """T -> F { (*|/) F }"""
        self.F()
        while not self.finished() and self.token_is(Token.TIMES, Token.DIVIDE):
            operator = self.token.token_type
            self.match(operator)
            self.F()
            self.evaluate_and_push(operator)

    def F(self):
        """F -> '(' E ')' | digit | identifier"""
        if self.token_is(Token.LEFT_PAREN):
            self.match(Token.LEFT_PAREN)
            self.E()
            self.match(Token.RIGHT_PAREN)
        elif self.token_is(Token.NUMBER):
            self.stack.append(self.token.lexeme_value)
            self.match(Token.NUMBER)
        elif self.token_is(Token.ID):
            self.stack.append(self.variables[self.token.lexeme_value])
            self.match(Token.ID)

    def print_result(self):
        print("%s = %.2f" % (self.expression, self.result))

# ------------------------ Tests --------------------------------#

status = {"OK": 0, "FAIL": 0}


def python_eval(expression, variables):
    variables.update({"pi": math.pi, "e": math.e})
    expression = ''.join(expression.split())
    if variables:
        # Need sorted by length (in reverse order) to replace variables whose name is "inside" others
        for key, value in sorted(variables.items(), key=lambda item: len(item[0]), reverse=True):
            expression = expression.replace(key, str(value))
    return float(eval(expression))


def test(expression, variables={}):
    """
        Test if expected value is equal to the evaluated value
    """
    returned = Parser().evaluate(expression, variables)
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
    test('1 + 2 - (2 + 2)')
    test('A + B / 2 - 9 * A + 14 * B', {"A": 9, "B": 10})
    test('a12C + e * 2  - b435 / pi - 9 * e - cde + 14 * fg123', {"a12C": 19.23, "b435": 29.123, "cde": -902.12, "fg123": 82.482})
    test("""1 +
            3 /
            4 - 9 * (3 - 2)
         """)
    print()
    count = status['OK'] + status['FAIL']
    print(("Status: OK = %.2f %%, FAIL = %.2f %%" %
          (status['OK']*100.00/count, status['FAIL']*100.00/count)))

if __name__ == "__main__":
    run()
