from ast import Assign
from ast import ClassDef
from ast import Load
from ast import Module
from ast import Name
from ast import Nonlocal
from ast import Store

tree = Module(
    body=[
        ClassDef(
            name="name_1",
            bases=[],
            keywords=[],
            body=[
                ClassDef(
                    name="name_0",
                    bases=[],
                    keywords=[],
                    body=[Nonlocal(names=["name_3"])],
                    decorator_list=[],
                ),
                Assign(
                    targets=[Name(id="name_3", ctx=Store())],
                    value=Name(id="name_1", ctx=Load()),
                ),
            ],
            decorator_list=[],
        )
    ],
    type_ignores=[],
)

# version: 3.10.8
#
# Source:
# class name_1:
#
#     class name_0:
#         nonlocal name_3
#     name_3 = name_1
#
#
# Error:
#     SyntaxError("no binding for nonlocal 'name_3' found")
