from ast import Expr
from ast import FormattedValue
from ast import Load
from ast import Module
from ast import Name

tree = Module(
    body=[
        Expr(
            value=FormattedValue(
                value=Name(id="name_0", ctx=Load()), conversion=-1, format_spec=None
            )
        )
    ],
    type_ignores=[],
)

# version: 3.8.16
#
#
# Error:
#     AttributeError("'FormattedValue' object has no attribute 'values'")
