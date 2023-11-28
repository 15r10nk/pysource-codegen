from ast import arguments
from ast import AsyncFunctionDef
from ast import FunctionDef
from ast import Load
from ast import Module
from ast import Name
from ast import Pass
from ast import Return
from ast import Yield

tree = Module(
    body=[
        AsyncFunctionDef(
            name="name_2",
            args=arguments(
                posonlyargs=[], args=[], kwonlyargs=[], kw_defaults=[], defaults=[]
            ),
            body=[
                FunctionDef(
                    name="name_4",
                    args=arguments(
                        posonlyargs=[],
                        args=[],
                        kwonlyargs=[],
                        kw_defaults=[],
                        defaults=[],
                    ),
                    body=[Pass()],
                    decorator_list=[],
                    returns=Yield(),
                ),
                Return(value=Name(id="name_0", ctx=Load())),
            ],
            decorator_list=[],
        )
    ],
    type_ignores=[],
)

# version: 3.9.15
# seed = 4392892
#
# Source:
# async def name_2():
#
#     def name_4() -> (yield):
#         pass
#     return name_0
#
#
# Error:
#     SyntaxError("'return' with value in async generator", ('<file>', 5, 5, None))
