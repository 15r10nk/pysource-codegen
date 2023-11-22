from ast import arg
from ast import arguments
from ast import AsyncFunctionDef
from ast import Attribute
from ast import BinOp
from ast import BitAnd
from ast import Call
from ast import Compare
from ast import comprehension
from ast import Constant
from ast import Dict
from ast import DictComp
from ast import FormattedValue
from ast import FunctionDef
from ast import GeneratorExp
from ast import IfExp
from ast import Invert
from ast import Is
from ast import JoinedStr
from ast import keyword
from ast import Lambda
from ast import List
from ast import ListComp
from ast import Load
from ast import Module
from ast import Name
from ast import NamedExpr
from ast import Not
from ast import Pass
from ast import Return
from ast import Set
from ast import SetComp
from ast import Store
from ast import Sub
from ast import Subscript
from ast import Tuple
from ast import UnaryOp
from ast import Yield

tree = Module(
    body=[
        AsyncFunctionDef(
            name="name_5",
            args=arguments(
                posonlyargs=[],
                args=[],
                kwonlyargs=[],
                kw_defaults=[
                    BinOp(
                        left=JoinedStr(
                            values=[
                                Constant(value=""),
                                Constant(value="", kind="some text"),
                                Constant(value=""),
                                FormattedValue(
                                    value=Name(id="name_1", ctx=Load()), conversion=115
                                ),
                                Constant(value=""),
                            ]
                        ),
                        op=BitAnd(),
                        right=BinOp(
                            left=Name(id="name_1", ctx=Load()),
                            op=Sub(),
                            right=Name(id="name_3", ctx=Load()),
                        ),
                    ),
                    GeneratorExp(
                        elt=Set(
                            elts=[
                                Name(id="name_0", ctx=Load()),
                                Name(id="name_5", ctx=Load()),
                            ]
                        ),
                        generators=[
                            comprehension(
                                target=List(
                                    elts=[Name(id="name_1", ctx=Store())], ctx=Store()
                                ),
                                iter=Tuple(
                                    elts=[Name(id="name_2", ctx=Load())], ctx=Load()
                                ),
                                ifs=[
                                    GeneratorExp(
                                        elt=Name(id="name_1", ctx=Load()),
                                        generators=[
                                            comprehension(
                                                target=Name(id="name_0", ctx=Store()),
                                                iter=Name(id="name_1", ctx=Load()),
                                                ifs=[Name(id="name_5", ctx=Load())],
                                                is_async=5,
                                            )
                                        ],
                                    ),
                                    Dict(
                                        keys=[Name(id="name_2", ctx=Load())],
                                        values=[Name(id="name_1", ctx=Load())],
                                    ),
                                    Constant(value=0),
                                ],
                                is_async=4,
                            ),
                            comprehension(
                                target=Subscript(
                                    value=Name(id="name_1", ctx=Load()),
                                    slice=Name(id="name_1", ctx=Load()),
                                    ctx=Store(),
                                ),
                                iter=UnaryOp(
                                    op=Invert(), operand=Name(id="name_4", ctx=Load())
                                ),
                                ifs=[
                                    Call(
                                        func=Name(id="name_5", ctx=Load()),
                                        args=[Name(id="name_1", ctx=Load())],
                                        keywords=[
                                            keyword(
                                                arg="name_0",
                                                value=Name(id="name_2", ctx=Load()),
                                            )
                                        ],
                                    ),
                                    SetComp(
                                        elt=Name(id="name_4", ctx=Load()),
                                        generators=[
                                            comprehension(
                                                target=Name(id="name_2", ctx=Store()),
                                                iter=Name(id="name_1", ctx=Load()),
                                                ifs=[Name(id="name_0", ctx=Load())],
                                                is_async=0,
                                            )
                                        ],
                                    ),
                                    Constant(value=""),
                                    Name(id="name_1", ctx=Load()),
                                    Name(id="name_2", ctx=Load()),
                                    Call(
                                        func=Name(id="name_1", ctx=Load()),
                                        args=[Name(id="name_3", ctx=Load())],
                                        keywords=[
                                            keyword(value=Name(id="name_4", ctx=Load()))
                                        ],
                                    ),
                                ],
                                is_async=3,
                            ),
                            comprehension(
                                target=Tuple(
                                    elts=[Name(id="name_3", ctx=Store())], ctx=Store()
                                ),
                                iter=Name(id="name_5", ctx=Load()),
                                ifs=[
                                    JoinedStr(values=[Constant(value="")]),
                                    GeneratorExp(
                                        elt=Name(id="name_1", ctx=Load()),
                                        generators=[
                                            comprehension(
                                                target=Name(id="name_2", ctx=Store()),
                                                iter=Name(id="name_4", ctx=Load()),
                                                ifs=[Name(id="name_3", ctx=Load())],
                                                is_async=4,
                                            )
                                        ],
                                    ),
                                    Dict(
                                        keys=[Name(id="name_4", ctx=Load())],
                                        values=[Name(id="name_3", ctx=Load())],
                                    ),
                                    Lambda(
                                        args=arguments(
                                            posonlyargs=[arg(arg="name_0")],
                                            args=[arg(arg="name_5")],
                                            kwonlyargs=[arg(arg="name_4")],
                                            kw_defaults=[Name(id="name_0", ctx=Load())],
                                            defaults=[Name(id="name_2", ctx=Load())],
                                        ),
                                        body=Name(id="name_4", ctx=Load()),
                                    ),
                                    Lambda(
                                        args=arguments(
                                            posonlyargs=[
                                                arg(arg="name_3", type_comment="")
                                            ],
                                            args=[arg(arg="name_0", type_comment="")],
                                            vararg=arg(arg="name_2", type_comment=""),
                                            kwonlyargs=[],
                                            kw_defaults=[Name(id="name_1", ctx=Load())],
                                            kwarg=arg(arg="name_1", type_comment=""),
                                            defaults=[Name(id="name_4", ctx=Load())],
                                        ),
                                        body=Name(id="name_3", ctx=Load()),
                                    ),
                                    Name(id="name_4", ctx=Load()),
                                ],
                                is_async=1,
                            ),
                        ],
                    ),
                    DictComp(
                        key=UnaryOp(op=Not(), operand=Name(id="name_0", ctx=Load())),
                        value=JoinedStr(
                            values=[
                                FormattedValue(
                                    value=Name(id="name_2", ctx=Load()),
                                    conversion=97,
                                    format_spec=JoinedStr(
                                        values=[
                                            FormattedValue(
                                                value=Name(id="name_1", ctx=Load()),
                                                conversion=115,
                                            )
                                        ]
                                    ),
                                ),
                                FormattedValue(
                                    value=Name(id="name_4", ctx=Load()), conversion=115
                                ),
                                FormattedValue(
                                    value=Name(id="name_3", ctx=Load()),
                                    conversion=115,
                                    format_spec=JoinedStr(values=[Constant(value="")]),
                                ),
                                FormattedValue(
                                    value=Name(id="name_5", ctx=Load()),
                                    conversion=115,
                                    format_spec=JoinedStr(
                                        values=[
                                            FormattedValue(
                                                value=Name(id="name_4", ctx=Load()),
                                                conversion=115,
                                            )
                                        ]
                                    ),
                                ),
                            ]
                        ),
                        generators=[
                            comprehension(
                                target=Name(id="name_5", ctx=Store()),
                                iter=SetComp(
                                    elt=Name(id="name_0", ctx=Load()),
                                    generators=[
                                        comprehension(
                                            target=Name(id="name_2", ctx=Store()),
                                            iter=Name(id="name_2", ctx=Load()),
                                            ifs=[Name(id="name_0", ctx=Load())],
                                            is_async=0,
                                        )
                                    ],
                                ),
                                ifs=[
                                    DictComp(
                                        key=Name(id="name_1", ctx=Load()),
                                        value=Name(id="name_0", ctx=Load()),
                                        generators=[
                                            comprehension(
                                                target=Name(id="name_4", ctx=Store()),
                                                iter=Name(id="name_5", ctx=Load()),
                                                ifs=[Name(id="name_2", ctx=Load())],
                                                is_async=0,
                                            )
                                        ],
                                    ),
                                    Name(id="name_2", ctx=Load()),
                                    UnaryOp(
                                        op=Invert(),
                                        operand=Name(id="name_4", ctx=Load()),
                                    ),
                                    Set(elts=[Name(id="name_4", ctx=Load())]),
                                ],
                                is_async=0,
                            ),
                            comprehension(
                                target=Attribute(
                                    value=Name(id="name_1", ctx=Load()),
                                    attr="name_4",
                                    ctx=Store(),
                                ),
                                iter=Constant(value=b""),
                                ifs=[
                                    Compare(
                                        left=Name(id="name_2", ctx=Load()),
                                        ops=[Is()],
                                        comparators=[Name(id="name_1", ctx=Load())],
                                    ),
                                    GeneratorExp(
                                        elt=Name(id="name_4", ctx=Load()),
                                        generators=[
                                            comprehension(
                                                target=Name(id="name_1", ctx=Store()),
                                                iter=Name(id="name_5", ctx=Load()),
                                                ifs=[Name(id="name_3", ctx=Load())],
                                                is_async=1,
                                            )
                                        ],
                                    ),
                                ],
                                is_async=0,
                            ),
                            comprehension(
                                target=Name(id="name_1", ctx=Store()),
                                iter=List(
                                    elts=[Name(id="name_2", ctx=Load())], ctx=Load()
                                ),
                                ifs=[
                                    Set(elts=[Name(id="name_4", ctx=Load())]),
                                    Attribute(
                                        value=Name(id="name_3", ctx=Load()),
                                        attr="name_5",
                                        ctx=Load(),
                                    ),
                                    IfExp(
                                        test=Name(id="name_2", ctx=Load()),
                                        body=Name(id="name_5", ctx=Load()),
                                        orelse=Name(id="name_2", ctx=Load()),
                                    ),
                                    ListComp(
                                        elt=Name(id="name_2", ctx=Load()),
                                        generators=[
                                            comprehension(
                                                target=Name(id="name_4", ctx=Store()),
                                                iter=Name(id="name_3", ctx=Load()),
                                                ifs=[Name(id="name_5", ctx=Load())],
                                                is_async=0,
                                            )
                                        ],
                                    ),
                                ],
                                is_async=0,
                            ),
                            comprehension(
                                target=List(
                                    elts=[Name(id="name_1", ctx=Store())], ctx=Store()
                                ),
                                iter=List(
                                    elts=[Name(id="name_0", ctx=Load())], ctx=Load()
                                ),
                                ifs=[
                                    Dict(
                                        keys=[Name(id="name_2", ctx=Load())],
                                        values=[Name(id="name_0", ctx=Load())],
                                    ),
                                    IfExp(
                                        test=Name(id="name_4", ctx=Load()),
                                        body=Name(id="name_4", ctx=Load()),
                                        orelse=Name(id="name_5", ctx=Load()),
                                    ),
                                    Lambda(
                                        args=arguments(
                                            posonlyargs=[arg(arg="name_4")],
                                            args=[
                                                arg(
                                                    arg="name_3",
                                                    type_comment="some text",
                                                )
                                            ],
                                            kwonlyargs=[arg(arg="name_2")],
                                            kw_defaults=[Name(id="name_4", ctx=Load())],
                                            defaults=[Name(id="name_0", ctx=Load())],
                                        ),
                                        body=Name(id="name_2", ctx=Load()),
                                    ),
                                    NamedExpr(
                                        target=Name(id="name_4", ctx=Load()),
                                        value=Name(id="name_5", ctx=Load()),
                                    ),
                                    ListComp(
                                        elt=Name(id="name_1", ctx=Load()),
                                        generators=[
                                            comprehension(
                                                target=Name(id="name_4", ctx=Store()),
                                                iter=Name(id="name_5", ctx=Load()),
                                                ifs=[Name(id="name_4", ctx=Load())],
                                                is_async=0,
                                            )
                                        ],
                                    ),
                                    List(
                                        elts=[Name(id="name_3", ctx=Load())], ctx=Load()
                                    ),
                                ],
                                is_async=0,
                            ),
                        ],
                    ),
                ],
                defaults=[],
            ),
            body=[
                Return(value=Name(id="name_0", ctx=Load())),
                FunctionDef(
                    name="name_3",
                    args=arguments(
                        posonlyargs=[arg(arg="name_0")],
                        args=[],
                        kwonlyargs=[],
                        kw_defaults=[
                            Constant(value=0),
                            Name(id="name_2", ctx=Load()),
                            IfExp(
                                test=Name(id="name_0", ctx=Load()),
                                body=Name(id="name_1", ctx=Load()),
                                orelse=Name(id="name_0", ctx=Load()),
                            ),
                        ],
                        defaults=[
                            Yield(),
                            JoinedStr(
                                values=[
                                    FormattedValue(
                                        value=Name(id="name_0", ctx=Load()),
                                        conversion=115,
                                    ),
                                    FormattedValue(
                                        value=Name(id="name_4", ctx=Load()),
                                        conversion=115,
                                    ),
                                    FormattedValue(
                                        value=Name(id="name_4", ctx=Load()),
                                        conversion=115,
                                        format_spec=JoinedStr(
                                            values=[Constant(value="", kind="")]
                                        ),
                                    ),
                                ]
                            ),
                            List(
                                elts=[
                                    Name(id="name_1", ctx=Load()),
                                    Name(id="name_4", ctx=Load()),
                                    Name(id="name_3", ctx=Load()),
                                    Name(id="name_1", ctx=Load()),
                                    Name(id="name_1", ctx=Load()),
                                    Name(id="name_5", ctx=Load()),
                                ],
                                ctx=Load(),
                            ),
                            List(
                                elts=[
                                    Name(id="name_5", ctx=Load()),
                                    Name(id="name_4", ctx=Load()),
                                    Name(id="name_4", ctx=Load()),
                                    Name(id="name_3", ctx=Load()),
                                ],
                                ctx=Load(),
                            ),
                        ],
                    ),
                    body=[Pass()],
                    decorator_list=[],
                ),
            ],
            decorator_list=[],
        )
    ],
    type_ignores=[],
)

# version: 3.9.15
#
# Source:
# async def name_5():
#     return name_0
#
#     def name_3(name_0=(yield), /):
#         pass
#
#
# Error:
#     SyntaxError("'return' with value in async generator", ('<file>', 2, 5, None))
