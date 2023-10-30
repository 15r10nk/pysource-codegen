from ast import arguments
from ast import AsyncFunctionDef
from ast import Await
from ast import Call
from ast import ClassDef
from ast import Compare
from ast import comprehension
from ast import Constant
from ast import Eq
from ast import Expr
from ast import GeneratorExp
from ast import IfExp
from ast import Invert
from ast import IsNot
from ast import keyword
from ast import ListComp
from ast import Load
from ast import Lt
from ast import Module
from ast import Name
from ast import NamedExpr
from ast import Store
from ast import Subscript
from ast import Tuple
from ast import UnaryOp

tree = Module(
    body=[
        AsyncFunctionDef(
            name="name_0",
            args=arguments(
                posonlyargs=[],
                args=[],
                kwonlyargs=[],
                kw_defaults=[
                    Compare(
                        left=IfExp(
                            test=Name(id="name_1", ctx=Load()),
                            body=Name(id="name_0", ctx=Load()),
                            orelse=Name(id="name_5", ctx=Load()),
                        ),
                        ops=[Lt(), Lt(), IsNot()],
                        comparators=[
                            NamedExpr(
                                target=Name(id="name_3", ctx=Load()),
                                value=Name(id="name_2", ctx=Load()),
                            ),
                            UnaryOp(op=Invert(), operand=Name(id="name_4", ctx=Load())),
                            Constant(value=""),
                            ListComp(
                                elt=Name(id="name_2", ctx=Load()),
                                generators=[
                                    comprehension(
                                        target=Name(id="name_1", ctx=Store()),
                                        iter=Name(id="name_5", ctx=Load()),
                                        ifs=[Name(id="name_2", ctx=Load())],
                                        is_async=0,
                                    ),
                                    comprehension(
                                        target=Name(id="name_0", ctx=Store()),
                                        iter=Name(id="name_3", ctx=Load()),
                                        ifs=[Name(id="name_5", ctx=Load())],
                                        is_async=0,
                                    ),
                                    comprehension(
                                        target=Name(id="name_3", ctx=Store()),
                                        iter=Name(id="name_4", ctx=Load()),
                                        ifs=[Name(id="name_3", ctx=Load())],
                                        is_async=0,
                                    ),
                                ],
                            ),
                            IfExp(
                                test=Name(id="name_0", ctx=Load()),
                                body=Name(id="name_1", ctx=Load()),
                                orelse=Name(id="name_5", ctx=Load()),
                            ),
                        ],
                    ),
                    Call(
                        func=NamedExpr(
                            target=Name(id="name_0", ctx=Load()),
                            value=Name(id="name_5", ctx=Load()),
                        ),
                        args=[
                            Tuple(
                                elts=[
                                    Name(id="name_4", ctx=Load()),
                                    Name(id="name_3", ctx=Load()),
                                    Name(id="name_4", ctx=Load()),
                                ],
                                ctx=Load(),
                            ),
                            Subscript(
                                value=Name(id="name_4", ctx=Load()),
                                slice=Name(id="name_1", ctx=Load()),
                                ctx=Load(),
                            ),
                            Compare(
                                left=Name(id="name_1", ctx=Load()),
                                ops=[Eq(), IsNot()],
                                comparators=[
                                    Name(id="name_3", ctx=Load()),
                                    Name(id="name_4", ctx=Load()),
                                    Name(id="name_4", ctx=Load()),
                                    Name(id="name_2", ctx=Load()),
                                ],
                            ),
                        ],
                        keywords=[
                            keyword(
                                arg="name_4",
                                value=GeneratorExp(
                                    elt=Name(id="name_3", ctx=Load()),
                                    generators=[
                                        comprehension(
                                            target=Name(id="name_2", ctx=Store()),
                                            iter=Name(id="name_3", ctx=Load()),
                                            ifs=[Name(id="name_5", ctx=Load())],
                                            is_async=0,
                                        )
                                    ],
                                ),
                            )
                        ],
                    ),
                ],
                defaults=[],
            ),
            body=[
                ClassDef(
                    name="name_4",
                    bases=[],
                    keywords=[],
                    body=[Expr(value=Await(value=Name(id="name_5", ctx=Load())))],
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
# async def name_0():
#
#     class name_4:
#         await name_5
#
#
# Error:
#     SyntaxError("'await' outside function", ('<file>', 4, 9, None, 4, 21))
