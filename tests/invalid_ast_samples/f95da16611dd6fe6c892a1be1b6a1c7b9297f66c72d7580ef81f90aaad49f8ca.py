from ast import arg
from ast import arguments
from ast import AsyncFunctionDef
from ast import Global
from ast import Load
from ast import Module
from ast import Name
from ast import Pass

tree = Module(
    body=[
        AsyncFunctionDef(
            name="name_3",
            args=arguments(
                posonlyargs=[],
                args=[arg(arg="name_4", annotation=Name(id="name_0", ctx=Load()))],
                kwonlyargs=[],
                kw_defaults=[
                    Name(id="name_5", ctx=Load()),
                    Name(id="name_1", ctx=Load()),
                ],
                defaults=[],
            ),
            body=[Pass()],
            decorator_list=[],
        ),
        Global(names=["name_0"]),
    ],
    type_ignores=[],
)

# version: 3.10.8
#
# Source:
# async def name_3(name_4: name_0):
#     pass
# global name_0
#
#
# Error:
#     SyntaxError("name 'name_0' is used prior to global declaration")
