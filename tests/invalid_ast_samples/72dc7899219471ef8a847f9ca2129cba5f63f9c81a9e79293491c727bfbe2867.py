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
            name="name_3",
            args=arguments(),
            body=[
                AsyncFunctionDef(
                    name="name_0",
                    args=arguments(),
                    body=[Pass()],
                    returns=SetComp(
                        elt=Name(id="name_0", ctx=Load()),
                        generators=[
                            comprehension(
                                target=Name(id="name_4", ctx=Store()),
                                iter=Name(id="name_3", ctx=Load()),
                                is_async=3,
                            )
                        ],
                    ),
                    type_params=[TypeVar(name="name_5")],
                )
            ],
        )
    ]
)

# version: 3.13.0b1
# seed = 1238331
#
# Source:
# async def name_3():
#
#     async def name_0[name_5]() -> {name_0 async for name_4 in name_3}:
#         pass
#
#
# Error:
#     SyntaxError('asynchronous comprehension outside of an asynchronous function', ('<file>', 3, 35, None, 3, 70))
