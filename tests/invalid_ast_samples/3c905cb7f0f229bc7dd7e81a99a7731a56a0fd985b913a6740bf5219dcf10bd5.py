from ast import AnnAssign
from ast import comprehension
from ast import Constant
from ast import DictComp
from ast import Module
from ast import Name
from ast import Set
from ast import Starred
from ast import Store

tree = Module(
    body=[
        AnnAssign(
            target=Name(id="unique_name_0", ctx=Store()),
            annotation=DictComp(
                key=Constant(value=0),
                value=Constant(value=0),
                generators=[
                    comprehension(
                        target=Starred(
                            value=Name(id="unique_name_1", ctx=Store()), ctx=Store()
                        ),
                        iter=Set(),
                        is_async=0,
                    )
                ],
            ),
            simple=1,
        )
    ]
)

# version: 3.14.3
# seed = 9584270354
#
# Source:
# unique_name_0: {0: 0 for *unique_name_1 in {*()}}
#
#
# Error:
#     SyntaxError('starred assignment target must be in a list or tuple', ('<file>', 1, 26, None, 1, 40))
