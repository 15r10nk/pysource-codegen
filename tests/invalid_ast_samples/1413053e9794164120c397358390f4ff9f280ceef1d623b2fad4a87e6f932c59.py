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
            name="name_0",
            args=arguments(
                posonlyargs=[
                    arg(arg="name_4", annotation=Name(id="name_4", ctx=Load()))
                ],
                args=[],
                kwonlyargs=[],
                kw_defaults=[],
                defaults=[],
            ),
            body=[Pass()],
            decorator_list=[],
            type_params=[],
        ),
        Global(names=["name_4"]),
    ],
    type_ignores=[],
)

# version: 3.12.0
# seed = 8529076
#
# Source:
# async def name_0(name_4: name_4, /):
#     pass
# global name_4
#
#
# Error:
#     SyntaxError("name 'name_4' is used prior to global declaration")
