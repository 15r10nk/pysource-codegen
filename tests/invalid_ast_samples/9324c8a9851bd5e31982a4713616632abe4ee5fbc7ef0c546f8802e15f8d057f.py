from ast import arguments
from ast import AsyncFunctionDef
from ast import comprehension
from ast import Constant
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
            name="name_5",
            args=arguments(),
            body=[
                AsyncFunctionDef(
                    name="name_2",
                    args=arguments(),
                    body=[Pass()],
                    type_params=[
                        TypeVar(
                            name="name_4",
                            default_value=ListComp(
                                elt=Constant(value=0),
                                generators=[
                                    comprehension(
                                        target=Name(id="unique_name_0", ctx=Store()),
                                        iter=Name(id="unique_name_1", ctx=Load()),
                                        is_async=3,
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

# version: 3.14.3
# seed = 6
#
# Source:
# async def name_5():
#
#     async def name_2[name_4 = [0 async for unique_name_0 in unique_name_1]]():
#         pass
#
#
# Error:
#     SyntaxError('asynchronous comprehension outside of an asynchronous function')
