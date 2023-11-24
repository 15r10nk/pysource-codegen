from ast import arg
from ast import arguments
from ast import ClassDef
from ast import Compare
from ast import comprehension
from ast import DictComp
from ast import FunctionDef
from ast import In
from ast import Lambda
from ast import Load
from ast import Module
from ast import Name
from ast import Nonlocal
from ast import Store
from ast import Subscript

tree = Module(
    body=[
        FunctionDef(
            name="name_3",
            args=arguments(
                posonlyargs=[],
                args=[],
                kwonlyargs=[],
                kw_defaults=[],
                defaults=[
                    Subscript(
                        value=Name(id="name_1", ctx=Load()),
                        slice=Name(id="name_1", ctx=Load()),
                        ctx=Load(),
                    ),
                    Compare(
                        left=Name(id="name_5", ctx=Load()),
                        ops=[In(), In(), In()],
                        comparators=[
                            Name(id="name_1", ctx=Load()),
                            Name(id="name_2", ctx=Load()),
                            Name(id="name_4", ctx=Load()),
                            Name(id="name_2", ctx=Load()),
                            Name(id="name_1", ctx=Load()),
                            Name(id="name_5", ctx=Load()),
                        ],
                    ),
                    Lambda(
                        args=arguments(
                            posonlyargs=[arg(arg="name_2", type_comment="some text")],
                            args=[arg(arg="name_1", type_comment="")],
                            kwonlyargs=[arg(arg="name_4", type_comment="")],
                            kw_defaults=[Name(id="name_3", ctx=Load())],
                            defaults=[Name(id="name_5", ctx=Load())],
                        ),
                        body=Name(id="name_1", ctx=Load()),
                    ),
                ],
            ),
            body=[
                ClassDef(
                    name="name_3",
                    bases=[],
                    keywords=[],
                    body=[Nonlocal(names=["name_4"])],
                    decorator_list=[
                        DictComp(
                            key=Name(id="name_2", ctx=Load()),
                            value=Name(id="name_5", ctx=Load()),
                            generators=[
                                comprehension(
                                    target=Name(id="name_4", ctx=Store()),
                                    iter=Name(id="name_3", ctx=Load()),
                                    ifs=[],
                                    is_async=0,
                                )
                            ],
                        )
                    ],
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
# def name_3():
#
#     @{name_2: name_5 for name_4 in name_3}
#     class name_3:
#         nonlocal name_4
#
#
# Error:
#     SyntaxError("no binding for nonlocal 'name_4' found")
# seed = 7904827
