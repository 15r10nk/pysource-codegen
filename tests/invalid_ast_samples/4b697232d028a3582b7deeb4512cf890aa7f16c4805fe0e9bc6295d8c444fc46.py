from ast import arguments
from ast import AsyncFunctionDef
from ast import Attribute
from ast import BinOp
from ast import Call
from ast import ClassDef
from ast import Compare
from ast import comprehension
from ast import Dict
from ast import FloorDiv
from ast import GeneratorExp
from ast import keyword
from ast import List
from ast import Load
from ast import Lt
from ast import LtE
from ast import Mod
from ast import Module
from ast import Name
from ast import NotIn
from ast import Return
from ast import Store
from ast import Sub
from ast import Subscript
from ast import Tuple

tree = Module(
    body=[
        AsyncFunctionDef(
            name="name_2",
            args=arguments(
                posonlyargs=[],
                args=[],
                kwonlyargs=[],
                kw_defaults=[
                    GeneratorExp(
                        elt=Compare(
                            left=Name(id="name_5", ctx=Load()),
                            ops=[Lt(), LtE()],
                            comparators=[
                                Name(id="name_0", ctx=Load()),
                                Name(id="name_4", ctx=Load()),
                            ],
                        ),
                        generators=[
                            comprehension(
                                target=Tuple(
                                    elts=[Name(id="name_2", ctx=Store())], ctx=Store()
                                ),
                                iter=Subscript(
                                    value=Name(id="name_5", ctx=Load()),
                                    slice=Name(id="name_3", ctx=Load()),
                                    ctx=Load(),
                                ),
                                ifs=[Name(id="name_4", ctx=Load())],
                                is_async=0,
                            ),
                            comprehension(
                                target=List(
                                    elts=[Name(id="name_1", ctx=Store())], ctx=Store()
                                ),
                                iter=Subscript(
                                    value=Name(id="name_4", ctx=Load()),
                                    slice=Name(id="name_3", ctx=Load()),
                                    ctx=Load(),
                                ),
                                ifs=[
                                    Attribute(
                                        value=Name(id="name_4", ctx=Load()),
                                        attr="name_4",
                                        ctx=Load(),
                                    ),
                                    BinOp(
                                        left=Name(id="name_3", ctx=Load()),
                                        op=Mod(),
                                        right=Name(id="name_4", ctx=Load()),
                                    ),
                                    Compare(
                                        left=Name(id="name_0", ctx=Load()),
                                        ops=[NotIn()],
                                        comparators=[Name(id="name_5", ctx=Load())],
                                    ),
                                    Dict(
                                        keys=[Name(id="name_3", ctx=Load())],
                                        values=[Name(id="name_4", ctx=Load())],
                                    ),
                                    BinOp(
                                        left=Name(id="name_1", ctx=Load()),
                                        op=FloorDiv(),
                                        right=Name(id="name_3", ctx=Load()),
                                    ),
                                    BinOp(
                                        left=Name(id="name_5", ctx=Load()),
                                        op=Sub(),
                                        right=Name(id="name_4", ctx=Load()),
                                    ),
                                ],
                                is_async=0,
                            ),
                            comprehension(
                                target=Attribute(
                                    value=Name(id="name_0", ctx=Load()),
                                    attr="name_5",
                                    ctx=Store(),
                                ),
                                iter=Name(id="name_0", ctx=Load()),
                                ifs=[
                                    Tuple(
                                        elts=[Name(id="name_4", ctx=Load())], ctx=Load()
                                    ),
                                    Call(
                                        func=Name(id="name_0", ctx=Load()),
                                        args=[Name(id="name_2", ctx=Load())],
                                        keywords=[
                                            keyword(
                                                arg="name_3",
                                                value=Name(id="name_5", ctx=Load()),
                                            )
                                        ],
                                    ),
                                    Dict(
                                        keys=[Name(id="name_5", ctx=Load())],
                                        values=[Name(id="name_5", ctx=Load())],
                                    ),
                                    Name(id="name_1", ctx=Load()),
                                ],
                                is_async=0,
                            ),
                        ],
                    )
                ],
                defaults=[],
            ),
            body=[
                ClassDef(
                    name="name_4",
                    bases=[],
                    keywords=[],
                    body=[Return(value=Name(id="name_2", ctx=Load()))],
                    decorator_list=[],
                    type_params=[],
                )
            ],
            decorator_list=[],
            type_params=[],
        )
    ],
    type_ignores=[],
)

# version: 3.12.0
#
# Source:
# async def name_2():
#
#     class name_4:
#         return name_2
#
#
# Error:
#     SyntaxError("'return' outside function", ('<file>', 4, 9, None, 4, 22))
