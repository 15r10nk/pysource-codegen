from ast import AnnAssign
from ast import arguments
from ast import AsyncFunctionDef
from ast import comprehension
from ast import Constant
from ast import Load
from ast import Module
from ast import Name
from ast import SetComp
from ast import Store

tree = Module(
    body=[
        AsyncFunctionDef(
            name="name_5",
            args=arguments(),
            body=[
                AnnAssign(
                    target=Name(id="unique_name_0", ctx=Store()),
                    annotation=SetComp(
                        elt=Constant(value=0),
                        generators=[
                            comprehension(
                                target=Name(id="unique_name_1", ctx=Store()),
                                iter=Name(id="unique_name_2", ctx=Load()),
                                is_async=2,
                            )
                        ],
                    ),
                    simple=1,
                )
            ],
        )
    ]
)

# version: 3.14.3
# seed = 8064705574
#
# Source:
# async def name_5():
#     unique_name_0: {0 async for unique_name_1 in unique_name_2}
#
#
# Error:
#     SyntaxError('asynchronous comprehension outside of an asynchronous function')
