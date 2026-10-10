import ast

x = ast.Constant(value=5)

print(ast.dump(ast.keyword(value=x)))

print(ast.dump(ast.keyword(arg=None, value=x)))
