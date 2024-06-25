from ast import arguments
from ast import AsyncFunctionDef
from ast import comprehension
from ast import Expr
from ast import Global
from ast import ListComp
from ast import Load
from ast import Module
from ast import Name
from ast import NamedExpr
from ast import Store

tree = Module(
    body=[
        AsyncFunctionDef(
            name="name_5",
            args=arguments(),
            body=[
                Expr(
                    value=ListComp(
                        elt=Name(id="name_3", ctx=Load()),
                        generators=[
                            comprehension(
                                target=Name(id="name_3", ctx=Store()),
                                iter=Name(id="name_5", ctx=Load()),
                                ifs=[
                                    NamedExpr(
                                        target=Name(id="name_1", ctx=Store()),
                                        value=Name(id="name_3", ctx=Load()),
                                    )
                                ],
                                is_async=0,
                            )
                        ],
                    )
                ),
                Global(names=["name_1"]),
            ],
        )
    ]
)

# version: 3.13.0b2+
# seed = 587
#
# Source:
# async def name_5():
#     [name_3 for name_3 in name_5 if (name_1 := name_3)]
#     global name_1
#
#
# Error:
#     SyntaxError("name 'name_1' is assigned to before global declaration")
