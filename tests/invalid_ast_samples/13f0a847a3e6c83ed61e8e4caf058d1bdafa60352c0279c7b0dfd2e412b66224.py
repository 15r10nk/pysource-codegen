from ast import Compare
from ast import comprehension
from ast import Expr
from ast import ListComp
from ast import Load
from ast import LtE
from ast import Module
from ast import Name

tree = Module(
    body=[
        Expr(
            value=ListComp(
                elt=Name(id="name_4", ctx=Load()),
                generators=[
                    comprehension(
                        target=Compare(
                            left=Name(id="name_1", ctx=Load()),
                            ops=[LtE()],
                            comparators=[Name(id="name_2", ctx=Load())],
                        ),
                        iter=Name(id="name_5", ctx=Load()),
                        ifs=[],
                        is_async=0,
                    )
                ],
            )
        )
    ],
    type_ignores=[],
)

# version: 3.12.0
#
# Source:
# [name_4 for name_1 <= name_2 in name_5]
#
#
# Error:
#     SyntaxError('invalid syntax', ('<file>', 1, 20, '[name_4 for name_1 <= name_2 in name_5]\n', 1, 22))
