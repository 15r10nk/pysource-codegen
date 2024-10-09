from ast import arguments
from ast import FunctionDef
from ast import Global
from ast import Module
from ast import Nonlocal

tree = Module(
    body=[
        FunctionDef(
            name="name_1",
            args=arguments(),
            body=[
                Global(names=["name_2"]),
                FunctionDef(
                    name="name_2", args=arguments(), body=[Nonlocal(names=["name_2"])]
                ),
            ],
        )
    ]
)

# version: 3.13.0b1
# seed = 2636981
#
# Source:
# def name_1():
#     global name_2
#
#     def name_2():
#         nonlocal name_2
#
#
# Error:
#     SyntaxError("no binding for nonlocal 'name_2' found")
