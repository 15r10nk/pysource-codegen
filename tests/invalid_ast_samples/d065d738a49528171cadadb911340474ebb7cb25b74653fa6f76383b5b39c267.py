from ast import arguments
from ast import AsyncFunctionDef
from ast import comprehension
from ast import Load
from ast import Module
from ast import Name
from ast import SetComp
from ast import Store
from ast import TypeAlias

tree = Module(
    body=[
        AsyncFunctionDef(
            name="name_0",
            args=arguments(),
            body=[
                TypeAlias(
                    name=Name(id="name_0", ctx=Store()),
                    value=SetComp(
                        elt=Name(id="name_3", ctx=Load()),
                        generators=[
                            comprehension(
                                target=Name(id="name_3", ctx=Store()),
                                iter=Name(id="name_2", ctx=Load()),
                                is_async=3,
                            )
                        ],
                    ),
                )
            ],
        )
    ]
)

# version: 3.13.0b1
# seed = 6246222
#
# Source:
# async def name_0():
#     type name_0 = {name_3 async for name_3 in name_2}
#
#
# Error:
#     SyntaxError('asynchronous comprehension outside of an asynchronous function', ('<file>', 2, 19, None, 2, 54))
