from ast import Compare
from ast import Expr
from ast import IsNot
from ast import List
from ast import Load
from ast import Lt
from ast import Module
from ast import Name
from ast import NotIn
from ast import Set
from ast import Starred

tree = Module(
    body=[
        Expr(
            value=List(
                elts=[
                    Compare(
                        left=Set(elts=[Name(id="name_1", ctx=Load())]),
                        ops=[NotIn(), IsNot(), Lt()],
                        comparators=[
                            Starred(value=Name(id="name_2", ctx=Load()), ctx=Load())
                        ],
                    )
                ],
                ctx=Load(),
            )
        )
    ],
    type_ignores=[],
)

# version: 3.12.0
#
# Source:
# [{name_1} not in *name_2]
#
#
# Error:
#     SyntaxError('invalid syntax', ('<file>', 1, 18, '[{name_1} not in *name_2]\n', 1, 19))
