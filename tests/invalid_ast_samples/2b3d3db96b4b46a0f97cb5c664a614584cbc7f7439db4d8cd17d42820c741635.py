from ast import ClassDef
from ast import comprehension
from ast import Expr
from ast import ListComp
from ast import Load
from ast import Module
from ast import Name
from ast import Nonlocal
from ast import Store

tree = Module(
    body=[
        ClassDef(
            name="name_3",
            bases=[],
            keywords=[],
            body=[
                Expr(
                    value=ListComp(
                        elt=Name(id="name_2", ctx=Load()),
                        generators=[
                            comprehension(
                                target=Name(id="name_1", ctx=Store()),
                                iter=Name(id="name_1", ctx=Load()),
                                ifs=[],
                                is_async=0,
                            )
                        ],
                    )
                ),
                ClassDef(
                    name="name_5",
                    bases=[],
                    keywords=[],
                    body=[Nonlocal(names=["name_1"])],
                    decorator_list=[],
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
# class name_3:
#     [name_2 for name_1 in name_1]
#
#     class name_5:
#         nonlocal name_1
#
#
# Error:
#     SyntaxError("no binding for nonlocal 'name_1' found")
