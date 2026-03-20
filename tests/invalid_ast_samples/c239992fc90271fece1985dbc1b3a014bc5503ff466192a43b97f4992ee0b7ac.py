from ast import comprehension
from ast import Constant
from ast import Expr
from ast import Module
from ast import Name
from ast import SetComp
from ast import Starred
from ast import Store

tree = Module(
    body=[
        Expr(
            value=SetComp(
                elt=Constant(value=0),
                generators=[
                    comprehension(
                        target=Starred(
                            value=Name(id="unique_name_0", ctx=Store()), ctx=Store()
                        ),
                        iter=Constant(value=0),
                        is_async=0,
                    )
                ],
            )
        )
    ]
)

# version: 3.14.0
# seed = 8153118600
#
# Source:
# {0 for *unique_name_0 in 0}
#
#
# Error:
#     SyntaxError('starred assignment target must be in a list or tuple', ('<file>', 1, 8, None, 1, 22))
