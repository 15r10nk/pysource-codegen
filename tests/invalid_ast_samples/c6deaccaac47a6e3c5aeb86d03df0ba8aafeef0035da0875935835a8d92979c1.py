from ast import arguments
from ast import AsyncFunctionDef
from ast import comprehension
from ast import Load
from ast import Module
from ast import Name
from ast import Pass
from ast import SetComp
from ast import Store
from ast import TypeVar

tree = Module(
    body=[
        AsyncFunctionDef(
            name="name_1",
            args=arguments(),
            body=[
                AsyncFunctionDef(
                    name="name_4",
                    args=arguments(),
                    body=[Pass()],
                    type_params=[
                        TypeVar(
                            name="name_1",
                            bound=SetComp(
                                elt=Name(id="name_4", ctx=Load()),
                                generators=[
                                    comprehension(
                                        target=Name(id="name_1", ctx=Store()),
                                        iter=Name(id="name_5", ctx=Load()),
                                        is_async=4,
                                    )
                                ],
                            ),
                        )
                    ],
                )
            ],
        )
    ]
)

# version: 3.13.0b1
# seed = 2128177
#
# Source:
# async def name_1():
#
#     async def name_4[name_1: {name_4 async for name_1 in name_5}]():
#         pass
#
#
# Error:
#     SyntaxError('asynchronous comprehension outside of an asynchronous function', ('<file>', 3, 30, None, 3, 65))
