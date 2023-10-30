from ast import comprehension
from ast import Constant
from ast import Dict
from ast import DictComp
from ast import Expr
from ast import JoinedStr
from ast import Load
from ast import Module
from ast import Name
from ast import NamedExpr
from ast import SetComp
from ast import Store
from ast import Subscript

tree = Module(
    body=[
        Expr(
            value=DictComp(
                key=Name(id="name_1", ctx=Load()),
                value=Dict(
                    keys=[
                        NamedExpr(
                            target=Name(id="name_4", ctx=Load()),
                            value=Name(id="name_2", ctx=Load()),
                        ),
                        JoinedStr(values=[Constant(value="text")]),
                        SetComp(
                            elt=Name(id="name_3", ctx=Load()),
                            generators=[
                                comprehension(
                                    target=Name(id="name_1", ctx=Store()),
                                    iter=Name(id="name_5", ctx=Load()),
                                    ifs=[Name(id="name_1", ctx=Load())],
                                    is_async=0,
                                )
                            ],
                        ),
                        Subscript(
                            value=Name(id="name_4", ctx=Load()),
                            slice=Name(id="name_4", ctx=Load()),
                            ctx=Load(),
                        ),
                    ],
                    values=[],
                ),
                generators=[
                    comprehension(
                        target=Constant(value="some const text"),
                        iter=Name(id="name_0", ctx=Load()),
                        ifs=[],
                        is_async=0,
                    )
                ],
            )
        )
    ],
    type_ignores=[],
)

# version: 3.12.0
#
# Source:
# {name_1: {} for 'some const text' in name_0}
#
#
# Error:
#     SyntaxError('cannot assign to literal', ('<file>', 1, 17, "{name_1: {} for 'some const text' in name_0}\n", 1, 34))
