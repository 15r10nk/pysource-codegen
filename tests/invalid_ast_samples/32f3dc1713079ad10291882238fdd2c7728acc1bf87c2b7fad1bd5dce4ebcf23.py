from ast import AnnAssign
from ast import JoinedStr
from ast import Load
from ast import Module
from ast import Name
from ast import Starred
from ast import Store
from ast import Subscript
from ast import Tuple

tree = Module(
    body=[
        AnnAssign(
            target=Subscript(
                value=JoinedStr(values=[]),
                slice=Tuple(
                    elts=[Starred(value=Name(id="name_3", ctx=Load()), ctx=Load())],
                    ctx=Load(),
                ),
                ctx=Store(),
            ),
            annotation=Name(id="name_3", ctx=Load()),
            simple=2,
        )
    ],
    type_ignores=[],
)

# version: 3.9.15
#
# Source:
# f''[(*name_3,)]: name_3
#
#
# Error:
#     SyntaxError("can't use starred expression here", ('<file>', 1, 6, None))
# seed = 9403548
