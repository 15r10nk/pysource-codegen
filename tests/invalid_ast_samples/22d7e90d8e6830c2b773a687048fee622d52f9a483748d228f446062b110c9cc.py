from ast import ClassDef
from ast import comprehension
from ast import GeneratorExp
from ast import keyword
from ast import Load
from ast import Module
from ast import Name
from ast import Nonlocal
from ast import Store

tree = Module(
    body=[
        ClassDef(
            name="name_4",
            bases=[],
            keywords=[],
            body=[
                ClassDef(
                    name="name_0",
                    bases=[],
                    keywords=[
                        keyword(
                            value=GeneratorExp(
                                elt=Name(id="name_5", ctx=Load()),
                                generators=[
                                    comprehension(
                                        target=Name(id="name_2", ctx=Store()),
                                        iter=Name(id="name_2", ctx=Load()),
                                        ifs=[],
                                        is_async=1,
                                    )
                                ],
                            )
                        )
                    ],
                    body=[Nonlocal(names=["name_2"])],
                    decorator_list=[],
                )
            ],
            decorator_list=[],
        )
    ],
    type_ignores=[],
)

# version: 3.10.8
#
# Source:
# class name_4:
#
#     class name_0(**(name_5 async for name_2 in name_2)):
#         nonlocal name_2
#
#
# Error:
#     SyntaxError("no binding for nonlocal 'name_2' found")
