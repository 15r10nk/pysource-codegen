from ast import arguments
from ast import AsyncFunctionDef
from ast import AsyncWith
from ast import Module
from ast import Pass

tree = Module(
    body=[
        AsyncFunctionDef(
            name="name_2",
            args=arguments(
                posonlyargs=[], args=[], kwonlyargs=[], kw_defaults=[], defaults=[]
            ),
            body=[AsyncWith(items=[], body=[Pass()])],
            decorator_list=[],
        )
    ],
    type_ignores=[],
)

# version: 3.9.15
# seed = 4634023
#
# Source:
# async def name_2():
#     async with :
#         pass
#
#
# Error:
#     SyntaxError('invalid syntax', ('<file>', 2, 16, '    async with :\n'))
