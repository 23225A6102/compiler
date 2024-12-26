import re
from flask import Flask, render_template, request

class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __repr__(self):
        return f"Token({self.type}, {self.value})"

class Lexer:
    def __init__(self, input_code):
        self.input_code = input_code
        self.tokens = []

    def tokenize(self):
        token_specification = [
            ('NUMBER', r'\d+(\.\d+)?'),  # Integer or decimal number
            ('PLUS', r'\+'),              # Addition operator
            ('MINUS', r'-'),               # Subtraction operator
            ('MULT', r'\*'),              # Multiplication operator
            ('DIV', r'/'),                 # Division operator
            ('LPAREN', r'\('),            # Left parenthesis
            ('RPAREN', r'\)'),            # Right parenthesis
            ('WHITESPACE', r'[ \t]+'),    # Skip whitespace
        ]

        token_regex = '|'.join(f'(?P<{pair[0]}>{pair[1]})' for pair in token_specification)
        for match in re.finditer(token_regex, self.input_code):
            kind = match.lastgroup
            value = match.group(kind)
            if kind == 'WHITESPACE':
                continue
            elif kind == 'NUMBER':
                value = float(value) if '.' in value else int(value)
            self.tokens.append(Token(kind, value))

        return self.tokens

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def parse(self):
        return self.expression()

    def expression(self):
        node = self.term()
        while self.current_token() and self.current_token().type in ('PLUS', 'MINUS'):
            op = self.current_token()
            self.advance()
            node = (op.value, node, self.term())
        return node

    def term(self):
        node = self.factor()
        while self.current_token() and self.current_token().type in ('MULT', 'DIV'):
            op = self.current_token()
            self.advance()
            node = (op.value, node, self.factor())
        return node

    def factor(self):
        token = self.current_token()
        if token.type == 'NUMBER':
            self.advance()
            return token.value
        elif token.type == 'LPAREN':
            self.advance()
            node = self.expression()
            self.advance()  # Skip RPAREN
            return node

    def current_token(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def advance(self):
        self.pos += 1

def format_tokens(tokens):
    table = "<table border='1'><tr><th>Type</th><th>Value</th></tr>"
    for token in tokens:
        table += f"<tr><td>{token.type}</td><td>{token.value}</td></tr>"
    table += "</table>"
    return table

def format_ast(ast, level=0):
    if not isinstance(ast, tuple) or len(ast) == 1:
        return "  " * level + str(ast) + "\n"
    if len(ast) == 3:
        operator = ast[0]
        left = format_ast(ast[1], level + 1)
        right = format_ast(ast[2], level + 1)
        return "  " * level + operator + "\n" + left + right
    return "  " * level + "Unknown Node\n"

# Flask Web Application
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    input_code = request.form['code']

    # Tokenization
    lexer = Lexer(input_code)
    tokens = lexer.tokenize()
    token_table = format_tokens(tokens)

    # Parsing
    parser = Parser(tokens)
    ast = parser.parse()
    ast_structure = "<pre>" + format_ast(ast) + "</pre>"

    return render_template('result.html', tokens=token_table, ast=ast_structure)

if __name__ == '__main__':
    app.run(debug=True)
