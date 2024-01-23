from ast import AnnAssign
from ast import Load
from ast import Module
from ast import Name
from ast import Store
from ast import Subscript

tree = Module(
    body=[
        AnnAssign(
            target=Subscript(
                value=Name(id="name_2", ctx=Load()),
                slice=Name(id="name_0", ctx=Load()),
                ctx=Store(),
            ),
            annotation=Name(id="name_4", ctx=Load()),
            value=Name(id="name_0", ctx=Load()),
            simple=1,
        )
    ],
    type_ignores=[],
)

# version: 3.12.0
# seed = 2668094
#
# Source:
# name_2[name_0]: name_4 = name_0
#
#
# Error:
#     TypeError('AnnAssign with simple non-Name target')
