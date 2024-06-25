from ast import arguments
from ast import FunctionDef
from ast import Load
from ast import Module
from ast import Name
from ast import NamedExpr
from ast import Pass
from ast import Store
from ast import TypeVar

tree = Module(
    body=[
        FunctionDef(
            name="name_5",
            args=arguments(),
            body=[Pass()],
            type_params=[
                TypeVar(
                    name="name_4",
                    bound=NamedExpr(
                        target=Name(id="name_4", ctx=Store()),
                        value=Name(id="name_5", ctx=Load()),
                    ),
                )
            ],
        )
    ]
)

# version: 3.13.0b1
# seed = 4793203
#
# Source:
# def name_5[name_4: (name_4 := name_5)]():
#     pass
#
#
# Error:
#     SyntaxError('named expression cannot be used within a TypeVar bound')
