from ast import comprehension
from ast import Expr
from ast import GeneratorExp
from ast import Global
from ast import Load
from ast import Module
from ast import Name
from ast import Store

tree = Module(
    body=[
        Expr(
            value=GeneratorExp(
                elt=Name(id="name_1", ctx=Load()),
                generators=[
                    comprehension(
                        target=Name(id="name_3", ctx=Store()),
                        iter=Name(id="name_3", ctx=Load()),
                        ifs=[],
                        is_async=0,
                    )
                ],
            )
        ),
        Global(names=["name_3"]),
    ],
    type_ignores=[],
)

# version: 3.10.8
#
# Source:
# (name_1 for name_3 in name_3)
# global name_3
#
#
# Error:
#     SyntaxError("name 'name_3' is used prior to global declaration")
