from ast import AugAssign
from ast import Div
from ast import Load
from ast import Module
from ast import Name

tree = Module(
    body=[
        AugAssign(
            target=Name(id="something", ctx=Load()),
            op=Div(),
            value=Name(id="name_2", ctx=Load()),
        )
    ],
    type_ignores=[],
)

# version: 3.12.0
# seed = 467504
#
# Source:
# something /= name_2
#
#
# Error:
#     ValueError('expression must have Store context but has Load instead')
