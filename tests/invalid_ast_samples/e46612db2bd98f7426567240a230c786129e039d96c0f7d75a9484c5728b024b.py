from ast import arguments
from ast import AsyncFunctionDef
from ast import Expr
from ast import Load
from ast import Module
from ast import Name
from ast import YieldFrom

tree = Module(
    body=[
        AsyncFunctionDef(
            name="name_2",
            args=arguments(
                posonlyargs=[], args=[], kwonlyargs=[], kw_defaults=[], defaults=[]
            ),
            body=[Expr(value=YieldFrom(value=Name(id="name_0", ctx=Load())))],
            decorator_list=[],
            type_params=[],
        )
    ],
    type_ignores=[],
)

# version: 3.12.0
#
# Source:
# async def name_2():
#     yield from name_0
#
#
# Error:
#     SyntaxError("'yield from' inside async function", ('<file>', 2, 5, None, 2, 22))
