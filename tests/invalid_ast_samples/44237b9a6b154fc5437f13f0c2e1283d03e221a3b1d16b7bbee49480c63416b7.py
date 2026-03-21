from ast import Assign
from ast import Attribute
from ast import Constant
from ast import Module
from ast import Store

tree = Module(
    body=[
        Assign(
            targets=[Attribute(value=Constant(value=0), attr="name_5", ctx=Store())],
            value=None,
        )
    ]
)

# version: 3.14.3
# seed = 1333901698
#
#
# Error:
#     AttributeError("'NoneType' object has no attribute '_fields'")
