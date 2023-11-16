from ast import arg
from ast import arguments
from ast import FunctionDef
from ast import Global
from ast import Load
from ast import Module
from ast import Name
from ast import Pass

tree = Module(
    body=[
        FunctionDef(
            name="name_3",
            args=arguments(
                posonlyargs=[],
                args=[arg(arg="name_4", annotation=Name(id="name_4", ctx=Load()))],
                kwonlyargs=[],
                kw_defaults=[],
                defaults=[],
            ),
            body=[Pass()],
            decorator_list=[],
        ),
        Global(names=["name_4"]),
    ],
    type_ignores=[],
)

# version: 3.10.8
#
# Source:
# def name_3(name_4: name_4):
#     pass
# global name_4
#
#
# Error:
#     SyntaxError("name 'name_4' is used prior to global declaration")
