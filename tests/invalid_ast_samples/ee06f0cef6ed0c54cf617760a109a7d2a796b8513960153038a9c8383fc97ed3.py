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
            name="name_0",
            args=arguments(
                posonlyargs=[],
                args=[
                    arg(
                        arg="name_3",
                        annotation=Name(id="name_5", ctx=Load()),
                        type_comment="some text",
                    )
                ],
                kwonlyargs=[],
                kw_defaults=[],
                defaults=[],
            ),
            body=[Pass()],
            decorator_list=[],
            type_params=[],
        ),
        Global(names=["name_5"]),
    ],
    type_ignores=[],
)

# version: 3.12.0
# seed = 774070
#
# Source:
# def name_0(name_3: name_5):
#     pass
# global name_5
#
#
# Error:
#     SyntaxError("name 'name_5' is used prior to global declaration")
