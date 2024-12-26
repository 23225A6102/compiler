from flask import Flask, render_template, request
from lexer_parser import Lexer, Parser, format_tokens, format_ast

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/process', methods=['POST'])
def process():
    input_code = request.form['code']
    lexer = Lexer(input_code)
    tokens = lexer.tokenize()

    # Generate Token Table
    token_table = format_tokens(tokens)

    # Parse the tokens
    parser = Parser(tokens)
    try:
        ast = parser.parse()
        ast_structure = format_ast(ast)
    except SyntaxError as e:
        ast_structure = f"Syntax Error: {e}"

    return render_template('result.html', token_table=token_table, ast_structure=ast_structure)


if __name__ == '__main__':
    app.run(debug=True)
