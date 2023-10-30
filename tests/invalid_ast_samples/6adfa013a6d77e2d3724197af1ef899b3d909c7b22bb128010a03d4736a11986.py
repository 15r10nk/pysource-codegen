from ast import arguments
from ast import AsyncFunctionDef
from ast import BinOp
from ast import comprehension
from ast import Constant
from ast import Dict
from ast import Expr
from ast import FormattedValue
from ast import GeneratorExp
from ast import IfExp
from ast import JoinedStr
from ast import List
from ast import Load
from ast import Mod
from ast import Module
from ast import Name
from ast import Set
from ast import SetComp
from ast import Store
from ast import Tuple
from ast import UnaryOp
from ast import USub
from ast import YieldFrom

tree = Module(
    body=[
        AsyncFunctionDef(
            name="name_4",
            args=arguments(
                posonlyargs=[],
                args=[],
                kwonlyargs=[],
                kw_defaults=[
                    SetComp(
                        elt=Name(id="name_3", ctx=Load()),
                        generators=[
                            comprehension(
                                target=Tuple(
                                    elts=[Name(id="name_0", ctx=Store())], ctx=Store()
                                ),
                                iter=Dict(
                                    keys=[Name(id="name_3", ctx=Load())],
                                    values=[Name(id="name_2", ctx=Load())],
                                ),
                                ifs=[
                                    BinOp(
                                        left=Name(id="name_0", ctx=Load()),
                                        op=Mod(),
                                        right=Name(id="name_5", ctx=Load()),
                                    )
                                ],
                                is_async=0,
                            ),
                            comprehension(
                                target=List(
                                    elts=[Name(id="name_0", ctx=Store())], ctx=Store()
                                ),
                                iter=Dict(
                                    keys=[Name(id="name_5", ctx=Load())],
                                    values=[Name(id="name_1", ctx=Load())],
                                ),
                                ifs=[
                                    JoinedStr(
                                        values=[
                                            FormattedValue(
                                                value=Name(id="name_4", ctx=Load()),
                                                conversion=-1,
                                            )
                                        ]
                                    ),
                                    Set(elts=[Name(id="name_3", ctx=Load())]),
                                    UnaryOp(
                                        op=USub(), operand=Name(id="name_1", ctx=Load())
                                    ),
                                ],
                                is_async=0,
                            ),
                            comprehension(
                                target=Name(id="name_5", ctx=Store()),
                                iter=IfExp(
                                    test=Name(id="name_1", ctx=Load()),
                                    body=Name(id="name_4", ctx=Load()),
                                    orelse=Name(id="name_0", ctx=Load()),
                                ),
                                ifs=[
                                    GeneratorExp(
                                        elt=Name(id="name_3", ctx=Load()),
                                        generators=[
                                            comprehension(
                                                target=Name(id="name_1", ctx=Store()),
                                                iter=Name(id="name_5", ctx=Load()),
                                                ifs=[Name(id="name_0", ctx=Load())],
                                                is_async=0,
                                            )
                                        ],
                                    )
                                ],
                                is_async=0,
                            ),
                        ],
                    ),
                    JoinedStr(
                        values=[
                            Constant(value="text"),
                            FormattedValue(
                                value=Name(id="name_1", ctx=Load()),
                                conversion=97,
                                format_spec=JoinedStr(
                                    values=[
                                        FormattedValue(
                                            value=Name(id="name_4", ctx=Load()),
                                            conversion=115,
                                            format_spec=JoinedStr(
                                                values=[Constant(value="text")]
                                            ),
                                        )
                                    ]
                                ),
                            ),
                            FormattedValue(
                                value=Name(id="name_2", ctx=Load()), conversion=-1
                            ),
                        ]
                    ),
                ],
                defaults=[],
            ),
            body=[Expr(value=YieldFrom(value=Name(id="name_5", ctx=Load())))],
            decorator_list=[],
            type_params=[],
        )
    ],
    type_ignores=[],
)

# version: 3.12.0
#
# Source:
# async def name_4():
#     yield from name_5
#
#
# Error:
#     SyntaxError("'yield from' inside async function", ('<file>', 2, 5, None, 2, 22))
