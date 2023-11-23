from ast import ClassDef
from ast import Global
from ast import Module
from ast import Pass

tree = Module(
    body=[
        ClassDef(
            name="name_0", bases=[], keywords=[], body=[Pass()], decorator_list=[]
        ),
        Global(names=["name_0"]),
    ],
    type_ignores=[],
)

# version: 3.10.8
#
# Source:
# class name_0:
#     pass
# global name_0
#
#
# Error:
#     SyntaxError("name 'name_0' is assigned to before global declaration")
# seed = 1826439
