from ast import arguments
from ast import AsyncFunctionDef
from ast import Constant
from ast import Expr
from ast import Load
from ast import Module
from ast import Name
from ast import YieldFrom

tree = Module(
    body=[
        AsyncFunctionDef(
            name="name_0",
            args=arguments(
                posonlyargs=[],
                args=[],
                kwonlyargs=[],
                kw_defaults=[Constant(value=1)],
                defaults=[],
            ),
            body=[Expr(value=YieldFrom(value=Name(id="name_3", ctx=Load())))],
            decorator_list=[],
            type_comment="",
        )
    ],
    type_ignores=[],
)

# Source:
# async def name_0(): # type:
#     yield from name_3
# Error:
#     SyntaxError("'yield from' inside async function", ('<file>', 2, 5, None, 2, 22))
