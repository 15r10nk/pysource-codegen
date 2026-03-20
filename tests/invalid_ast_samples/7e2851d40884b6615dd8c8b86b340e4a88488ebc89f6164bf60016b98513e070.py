from ast import arguments
from ast import AsyncFunctionDef
from ast import Await
from ast import Constant
from ast import Module
from ast import Name
from ast import Store
from ast import TypeAlias

tree = Module(
    body=[
        AsyncFunctionDef(
            name="name_1",
            args=arguments(),
            body=[
                TypeAlias(
                    name=Name(id="unique_name_0", ctx=Store()),
                    value=Await(value=Constant(value=0)),
                )
            ],
        )
    ]
)

# version: 3.14.0
# seed = 8858508848
#
# Source:
# async def name_1():
#     type unique_name_0 = await 0
#
#
# Error:
#     SyntaxError('await expression cannot be used within a type alias')
