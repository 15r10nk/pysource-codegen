from ast import arguments
from ast import AsyncFunctionDef
from ast import Continue
from ast import Module

tree = Module(
    body=[
        AsyncFunctionDef(
            name="name_2",
            args=arguments(
                posonlyargs=[], args=[], kwonlyargs=[], kw_defaults=[], defaults=[]
            ),
            body=[Continue()],
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
#     continue
#
#
# Error:
#     SyntaxError("'continue' not properly in loop", ('<file>', 2, 5, None, 2, 13))
