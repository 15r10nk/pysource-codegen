from ast import BoolOp
from ast import Expr
from ast import Load
from ast import Module
from ast import Name
from ast import Or
from ast import Slice
from ast import Starred
from ast import Store
from ast import Subscript
from ast import Tuple

tree = Module(
    body=[
        Expr(
            value=Subscript(
                value=BoolOp(
                    op=Or(),
                    values=[
                        Name(id="name_2", ctx=Load()),
                        Name(id="name_0", ctx=Load()),
                    ],
                ),
                slice=Tuple(
                    elts=[
                        Slice(upper=Name(id="name_3", ctx=Load())),
                        Starred(value=Name(id="name_4", ctx=Load()), ctx=Load()),
                    ],
                    ctx=Load(),
                ),
                ctx=Store(),
            )
        )
    ],
    type_ignores=[],
)

# version: 3.10.8
#
# Source:
# (name_2 or name_0)[(:name_3, *name_4)]
#
#
# Error:
#     SyntaxError('invalid syntax', ('<file>', 1, 21, '(name_2 or name_0)[(:name_3, *name_4)]\n', 1, 22))
