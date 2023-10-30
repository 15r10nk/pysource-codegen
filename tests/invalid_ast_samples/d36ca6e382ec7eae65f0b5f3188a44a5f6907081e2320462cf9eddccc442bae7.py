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
                    posonlyargs=[arg(arg="name_3", type_comment="some text")],
                    args=[],
                    vararg=arg(arg="name_3", type_comment=""),
                    kwonlyargs=[],
                    kw_defaults=[],
                    defaults=[],
                ),
                body=Name(id="name_4", ctx=Load()),
            )
        )
    ],
    type_ignores=[],
)

# version: 3.12.0
#
# Source:
# lambda name_3, /, *name_3: name_4
#
#
# Error:
#     SyntaxError("duplicate argument 'name_3' in function definition")
