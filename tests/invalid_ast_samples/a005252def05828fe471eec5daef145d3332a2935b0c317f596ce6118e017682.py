from ast import arguments
from ast import Compare
from ast import FunctionDef
from ast import Gt
from ast import Is
from ast import Load
from ast import Lt
from ast import LtE
from ast import Module
from ast import Name
from ast import NamedExpr
from ast import Pass
from ast import Tuple
from ast import TypeVar

tree = Module(
    body=[
        FunctionDef(
            name="name_0",
            args=arguments(
                posonlyargs=[],
                args=[],
                kwonlyargs=[],
                kw_defaults=[
                    Tuple(
                        elts=[
                            Name(id="name_2", ctx=Load()),
                            Name(id="name_4", ctx=Load()),
                            Name(id="name_5", ctx=Load()),
                            Name(id="name_3", ctx=Load()),
                            Name(id="name_3", ctx=Load()),
                            Name(id="name_2", ctx=Load()),
                        ],
                        ctx=Load(),
                    ),
                    Compare(
                        left=Name(id="name_0", ctx=Load()),
                        ops=[Gt(), LtE(), Lt(), Gt(), Is()],
                        comparators=[
                            Name(id="name_3", ctx=Load()),
                            Name(id="name_0", ctx=Load()),
                            Name(id="name_4", ctx=Load()),
                        ],
                    ),
                ],
                defaults=[],
            ),
            body=[Pass()],
            decorator_list=[],
            type_params=[
                TypeVar(
                    name="name_2",
                    bound=NamedExpr(
                        target=Name(id="name_3", ctx=Load()),
                        value=Name(id="name_3", ctx=Load()),
                    ),
                )
            ],
        )
    ],
    type_ignores=[],
)

# version: 3.12.0
#
# Source:
# def name_0[name_2: (name_3 := name_3)]():
#     pass
#
#
# Error:
#     SyntaxError('named expression cannot be used within a TypeVar bound')
