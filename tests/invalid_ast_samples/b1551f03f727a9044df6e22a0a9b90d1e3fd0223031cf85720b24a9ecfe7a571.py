from ast import AsyncWith
from ast import Load
from ast import Module
from ast import Name
from ast import Pass
from ast import withitem

tree = Module(
    body=[
        AsyncWith(
            items=[withitem(context_expr=Name(id="name_1", ctx=Load()))], body=[Pass()]
        )
    ],
    type_ignores=[],
)

# Source:
# async with name_1:
#     pass
# Error:
#     SyntaxError("'async with' outside async function", ('<file>', 1, 1, None, 2, 9))
