from ast import AnnAssign
from ast import Attribute
from ast import Compare
from ast import Load
from ast import Module
from ast import Name
from ast import Store

tree = Module(
    body=[
        AnnAssign(
            target=Attribute(
                value=Compare(
                    left=Name(id="name_5", ctx=Load()), ops=[], comparators=[]
                ),
                attr="name_3",
                ctx=Store(),
            ),
            annotation=Name(id="name_4", ctx=Load()),
            simple=3,
        )
    ],
    type_ignores=[],
)

# version: 3.9.15
# seed = 3589045
#
# Source:
# (name_5).name_3: name_4
#
#
# Error:
#     SyntaxError('illegal target for annotation', ('<file>', 1, 1, '(name_5).name_3: name_4\n'))
