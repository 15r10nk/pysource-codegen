from ast import Expr
from ast import FormattedValue
from ast import JoinedStr
from ast import Load
from ast import Module
from ast import Name

tree = Module(
    body=[
        Expr(
            value=JoinedStr(
                values=[
                    FormattedValue(
                        value=Name(id="name_3", ctx=Load()),
                        conversion=114,
                        format_spec=Name(id="name_4", ctx=Load()),
                    )
                ]
            )
        )
    ],
    type_ignores=[],
)

# version: 3.12.0
#
#
# Error:
#     ValueError('Unexpected node inside JoinedStr, <ast.Name object at 0x7f18961470d0>')
