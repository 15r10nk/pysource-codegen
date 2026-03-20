from ast import comprehension
from ast import Constant
from ast import DictComp
from ast import Expr
from ast import Module
from ast import Name
from ast import Store

tree = Module(
    body=[
        Expr(
            value=DictComp(
                key=Constant(value=0),
                generators=[
                    comprehension(
                        target=Name(id="unique_name_0", ctx=Store()),
                        iter=Name(id="unique_name_1"),
                        is_async=0,
                    )
                ],
            )
        )
    ]
)

# version: 3.15.0a6
# seed = 462738884
#
#
# Error:
#     AttributeError("'NoneType' object has no attribute '_fields'")
