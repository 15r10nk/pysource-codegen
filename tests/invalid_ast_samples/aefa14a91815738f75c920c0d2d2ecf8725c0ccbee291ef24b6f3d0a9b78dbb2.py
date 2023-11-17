from ast import arguments
from ast import AsyncFunctionDef
from ast import Attribute
from ast import BoolOp
from ast import ExceptHandler
from ast import FunctionDef
from ast import Load
from ast import Module
from ast import Name
from ast import Or
from ast import Pass
from ast import Return
from ast import Try
from ast import Yield

tree = Module(
    body=[
        AsyncFunctionDef(
            name="name_3",
            args=arguments(
                posonlyargs=[],
                args=[],
                kwonlyargs=[],
                kw_defaults=[
                    Attribute(
                        value=BoolOp(
                            op=Or(),
                            values=[
                                Name(id="name_1", ctx=Load()),
                                Name(id="name_4", ctx=Load()),
                                Name(id="name_3", ctx=Load()),
                                Name(id="name_2", ctx=Load()),
                            ],
                        ),
                        attr="name_3",
                        ctx=Load(),
                    )
                ],
                defaults=[],
            ),
            body=[
                Try(
                    body=[Return(value=Name(id="name_5", ctx=Load()))],
                    handlers=[ExceptHandler(body=[Pass()])],
                    orelse=[],
                    finalbody=[
                        FunctionDef(
                            name="name_3",
                            args=arguments(
                                posonlyargs=[],
                                args=[],
                                kwonlyargs=[],
                                kw_defaults=[
                                    Name(id="name_1", ctx=Load()),
                                    Name(id="name_3", ctx=Load()),
                                    Name(id="name_0", ctx=Load()),
                                    Name(id="name_0", ctx=Load()),
                                    Name(id="name_3", ctx=Load()),
                                ],
                                defaults=[],
                            ),
                            body=[Pass()],
                            decorator_list=[Yield()],
                        )
                    ],
                )
            ],
            decorator_list=[],
        )
    ],
    type_ignores=[],
)

# version: 3.10.8
#
# Source:
# async def name_3():
#     try:
#         return name_5
#     except:
#         pass
#     finally:
#
#         @(yield)
#         def name_3():
#             pass
#
#
# Error:
#     SyntaxError("'return' with value in async generator", ('<file>', 3, 9, None, 3, 22))
