from ast import arguments
from ast import Continue
from ast import FunctionDef
from ast import Load
from ast import Module
from ast import Name
from ast import While

tree = Module(
    body=[
        While(
            test=Name(id="name_0", ctx=Load()),
            body=[
                FunctionDef(
                    name="name_4",
                    args=arguments(
                        posonlyargs=[],
                        args=[],
                        kwonlyargs=[],
                        kw_defaults=[
                            Name(id="name_2", ctx=Load()),
                            Name(id="name_1", ctx=Load()),
                            Name(id="name_0", ctx=Load()),
                            Name(id="name_0", ctx=Load()),
                            Name(id="name_2", ctx=Load()),
                        ],
                        defaults=[],
                    ),
                    body=[Continue()],
                    decorator_list=[],
                    type_params=[],
                )
            ],
            orelse=[],
        )
    ],
    type_ignores=[],
)

# version: 3.12.0
#
# Source:
# while name_0:
#
#     def name_4():
#         continue
#
#
# Error:
#     SyntaxError("'continue' not properly in loop", ('<file>', 4, 9, None, 4, 17))
