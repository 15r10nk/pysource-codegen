from ast import arg
from ast import arguments
from ast import Expr
from ast import Lambda
from ast import Load
from ast import Module
from ast import Name

tree = Module(
    body=[
        Expr(
            value=Lambda(
                args=arguments(
                    posonlyargs=[],
                    args=[],
                    kwonlyargs=[arg(arg="name_2")],
                    kw_defaults=[Name(id="name_2", ctx=Load())],
                    kwarg=arg(arg="name_2", type_comment=""),
                    defaults=[],
                ),
                body=Name(id="name_0", ctx=Load()),
            )
        )
    ],
    type_ignores=[],
)

# version: 3.12.0
#
# Source:
# lambda *, name_2=name_2, **name_2: name_0
#
#
# Error:
#     SyntaxError("duplicate argument 'name_2' in function definition")
