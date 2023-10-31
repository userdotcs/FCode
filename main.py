import runner, lexer, prsr, os#, json

while True:
    s = input(">> ")
    print(s)
    f = open(s)
    runner.project_path = os.path.dirname(s)
    tokens = lexer.Lexer(f.read().replace("\n", " "), f.name).lex()
    parser = prsr.Parser(tokens, f.name)
    ast = parser.expression()
    # print(json.dumps(ast, indent=3))
    runner.Runner(ast, f.name).run()
    runner.modules = {}
