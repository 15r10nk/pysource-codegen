from ast import arg
from ast import arguments
from ast import AsyncFunctionDef
from ast import comprehension
from ast import ListComp
from ast import Load
from ast import Module
from ast import Name
from ast import Pass
from ast import Store
from ast import TypeVar

tree = Module(
    body=[
        AsyncFunctionDef(
            name="name_2",
            args=arguments(),
            body=[
                AsyncFunctionDef(
                    name="name_5",
                    args=arguments(
                        kwonlyargs=[
                            arg(
                                arg="name_1",
                                annotation=ListComp(
                                    elt=Name(id="name_4", ctx=Load()),
                                    generators=[
                                        comprehension(
                                            target=Name(id="name_3", ctx=Store()),
                                            iter=Name(id="name_4", ctx=Load()),
                                            is_async=3,
                                        )
                                    ],
                                ),
                            )
                        ],
                        kw_defaults=[None],
                    ),
                    body=[Pass()],
                    type_params=[TypeVar(name="name_3")],
                )
            ],
        )
    ]
)

# version: 3.13.0b1
# seed = 6570464
#
# Source:
# async def name_2():
#
#     async def name_5[name_3](*, name_1: [name_4 async for name_3 in name_4]):
#         pass
#
#
# Error:
#     SyntaxError('asynchronous comprehension outside of an asynchronous function', ('<file>', 3, 41, None, 3, 76))
