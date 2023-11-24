from ast import AnnAssign
from ast import arg
from ast import arguments
from ast import ClassDef
from ast import FunctionDef
from ast import Load
from ast import Module
from ast import Name
from ast import Nonlocal
from ast import Store

tree = Module(
    body=[
        FunctionDef(
            name="name_3",
            args=arguments(
                posonlyargs=[],
                args=[],
                kwonlyargs=[arg(arg="name_3")],
                kw_defaults=[None],
                defaults=[],
            ),
            body=[
                ClassDef(
                    name="name_4",
                    bases=[],
                    keywords=[],
                    body=[
                        Nonlocal(names=["name_3"]),
                        AnnAssign(
                            target=Name(id="name_3", ctx=Store()),
                            annotation=Name(id="name_5", ctx=Load()),
                            value=Name(id="name_1", ctx=Load()),
                            simple=2,
                        ),
                    ],
                    decorator_list=[],
                )
            ],
            decorator_list=[],
        )
    ],
    type_ignores=[],
)

# version: 3.9.15
#
# Source:
# def name_3(*, name_3):
#
#     class name_4:
#         nonlocal name_3
#         name_3: name_5 = name_1
#
#
# Error:
#     SyntaxError("annotated name 'name_3' can't be nonlocal")
# seed = 5322869
