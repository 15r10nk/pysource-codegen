from ast import arg
from ast import arguments
from ast import ClassDef
from ast import FunctionDef
from ast import Global
from ast import Module
from ast import Nonlocal

tree = Module(
    body=[
        FunctionDef(
            name="name_5",
            args=arguments(
                posonlyargs=[],
                args=[],
                vararg=None,
                kwonlyargs=[
                    arg(arg="name_4", annotation=None, type_comment="some text")
                ],
                kw_defaults=[None],
                kwarg=None,
                defaults=[],
            ),
            body=[
                ClassDef(
                    name="name_5",
                    bases=[],
                    keywords=[],
                    body=[Global(names=["name_4"]), Nonlocal(names=["name_4"])],
                    decorator_list=[],
                )
            ],
            decorator_list=[],
            returns=None,
            type_comment=None,
        )
    ],
    type_ignores=[],
)

# version: 3.8.16
# seed = 6589600
#
# Source:
#
#
# def name_5(*, name_4):
#
#     class name_5():
#         global name_4
#         nonlocal name_4
#
#
#
# Error:
#     SyntaxError("name 'name_4' is nonlocal and global")
