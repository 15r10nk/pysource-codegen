from ast import arguments
from ast import ClassDef
from ast import comprehension
from ast import FunctionDef
from ast import Load
from ast import Module
from ast import Name
from ast import Nonlocal
from ast import SetComp
from ast import Store

tree = Module(
    body=[
        FunctionDef(
            name="name_4",
            args=arguments(
                posonlyargs=[], args=[], kwonlyargs=[], kw_defaults=[], defaults=[]
            ),
            body=[
                ClassDef(
                    name="name_1",
                    bases=[
                        SetComp(
                            elt=Name(id="name_3", ctx=Load()),
                            generators=[
                                comprehension(
                                    target=Name(id="name_0", ctx=Store()),
                                    iter=Name(id="name_5", ctx=Load()),
                                    ifs=[],
                                    is_async=0,
                                )
                            ],
                        )
                    ],
                    keywords=[],
                    body=[Nonlocal(names=["name_0"])],
                    decorator_list=[],
                )
            ],
            decorator_list=[],
        )
    ],
    type_ignores=[],
)

# version: 3.9.15
# seed = 4500971
#
# Source:
# def name_4():
#
#     class name_1({name_3 for name_0 in name_5}):
#         nonlocal name_0
#
#
# Error:
#     SyntaxError("no binding for nonlocal 'name_0' found")
