class Token:

    (ID, NUMBER, PLUS, MINUS, TIMES, DIVIDE, LEFT_PAREN, RIGHT_PAREN) = range(8)

    dict_token_type = {
        ID: "identifier",
        NUMBER: 'number',
        PLUS: 'operator "+"',
        MINUS: 'operator "-"',
        TIMES: 'operator "*"',
        DIVIDE: 'operator "/"',
        LEFT_PAREN: 'left parenthesis',
        RIGHT_PAREN: 'right parenthesis'
    }

    def __init__(self, token_type, lexeme, lexeme_value=None):
        self.token_type = token_type
        self.lexeme = lexeme
        self.lexeme_value = lexeme_value

    def __repr__(self):
        return ("Token type: %8s | Lexeme = %s | Lexeme value = %s" %
                (str(self.dict_token_type[self.token_type]), self.lexeme, str(self.lexeme_value)))


class Lexer:

    tokens = []
    index = 0
    symbols = '+-*/()'

    def __init__(self, expression):
        self.expression = expression

    def finish(self):
        return self.index >= len(self.expression)

    def get_char(self):
        if not self.finish():
            self.index += 1
            return self.expression[self.index - 1]
        return None

    def peek(self):
        if not self.finish():
            return self.expression[self.index]

    def skip_spaces(self):
        while not self.finish() and self.expression[self.index] == ' ':
            self.index += 1

    def read_number(self):
        lexeme = ""
        while not self.finish():
            c = self.peek()
            if (lexeme + c).isnumeric():
                lexeme += self.get_char()
            else:
                break
        if lexeme:
            return Token(Token.NUMBER, lexeme, float(lexeme))

    def read_symbol(self):
        if not self.finish() and self.peek() in self.symbols:
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

    def tokenize(self):
        self.tokens.clear()
        while not self.finish():
            self.skip_spaces()
            token = self.read_number()
            if token:
                self.tokens.append(token)
            token = self.read_symbol()
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

    stack = []
    result = 0.0
    tokens = []
    index = 0
    finish = False
    token = None

    def evaluate(self, expression):
        self.expression = expression
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
        return self.token.token_type in list(token_types)

    def finish(self):
        return self.index >= len(self.tokens)

    def next_token(self):
        if not self.finish():
            self.index += 1
            return self.tokens[self.index - 1]

    def match(self, token_type_expected):
        if not self.token_is(token_type_expected):
            raise (ValueError('Syntax error: expected %s but got %s' %
                              str(token_type_expected), str(self.token)))
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
                raise ValueError("Semantic error: Divion by zero")
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
        while not self.finish() and self.token_is(Token.PLUS, Token.MINUS):
            operator = self.token.token_type
            self.match(operator)
            self.T()
            self.evaluate_and_push(operator)

    def T(self):
        """T -> F { (*|/) F }"""
        self.F()
        while not self.finish() and self.token_is(Token.TIMES, Token.DIVIDE):
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
        else:
            pass
            #self.match(Token.ID)

    def print_result(self):
        print("%s = %.2f" % (self.expression, self.result))


def test_expression(expression):
    p = Parser()
    p.evaluate(expression)
    p.print_result()


def run():
    test_expression('123 + 987  * 230984 / (1 + 2)')
    test_expression('8 / 3 * 2')
    test_expression('2 + (((3 - 2)) * 7)')

if __name__ == "__main__":
    run()
