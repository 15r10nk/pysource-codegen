from ast import Assign
from ast import List
from ast import Load
from ast import Module
from ast import Name
from ast import Starred
from ast import Store

tree = Module(
    body=[
        Assign(
            targets=[
                List(
                    elts=[
                        Starred(value=Name(id="name_3", ctx=Store()), ctx=Store()),
                        Starred(value=Name(id="name_5", ctx=Store()), ctx=Store()),
                    ],
                    ctx=Store(),
                )
            ],
            value=Name(id="name_3", ctx=Load()),
        )
    ],
    type_ignores=[],
)

# version: 3.12.0
#
# Source:
# [*name_3, *name_5] = name_3
#
#
# Error:
#     SyntaxError('multiple starred expressions in assignment', ('<file>', 1, 1, None, 1, 19))
