from ast import *

tree = Module(
    body=[
        Delete(
            targets=[
                Compare(
                    left=Name(id="name_5", ctx=Load()),
                    ops=[GtE(), IsNot()],
                    comparators=[Name(id="name_5", ctx=Load())],
                )
            ]
        )
    ],
    type_ignores=[],
)

# version: 3.12.0
#
# Source:
# del name_5 >= name_5
#
#
# Error:
#     SyntaxError('cannot delete comparison', ('<file>', 1, 5, 'del name_5 >= name_5\n', 1, 21))
