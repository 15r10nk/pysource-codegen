from ast import Await
from ast import BoolOp
from ast import comprehension
from ast import Dict
from ast import Expr
from ast import GeneratorExp
from ast import Load
from ast import Module
from ast import Name
from ast import Or
from ast import Store
from ast import Subscript
from ast import Tuple

tree = Module(
    body=[
        Expr(
            value=GeneratorExp(
                elt=Dict(),
                generators=[
                    comprehension(
                        target=Subscript(
                            value=Name(id="name_1", ctx=Load()),
                            slice=BoolOp(
                                op=Or(),
                                values=[
                                    Name(id="name_2", ctx=Load()),
                                    Name(id="name_0", ctx=Load()),
                                ],
                            ),
                            ctx=Store(),
                        ),
                        iter=Await(value=Tuple(ctx=Load())),
                        is_async=0,
                    )
                ],
            )
        )
    ]
)

# version: 3.13.0b1
# seed = 3002626
#
# Source:
# ({} for name_1[name_2 or name_0] in await ())
#
#
# Error:
#     SyntaxError("'await' outside function", ('<file>', 1, 37, None, 1, 45))
