from ast import Break
from ast import ClassDef
from ast import Load
from ast import Module
from ast import Name
from ast import While

tree = Module(
    body=[
        While(
            test=Name(id="name_0", ctx=Load()),
            body=[
                ClassDef(
                    name="name_4",
                    bases=[],
                    keywords=[],
                    body=[Break()],
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
#     class name_4:
#         break
#
#
# Error:
#     SyntaxError("'break' outside loop", ('<file>', 4, 9, None, 4, 14))
