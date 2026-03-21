from ast import comprehension
from ast import Constant
from ast import Load
from ast import Module
from ast import Name
from ast import SetComp
from ast import Starred
from ast import Store
from ast import Tuple
from ast import TypeAlias

tree = Module(
    body=[
        TypeAlias(
            name=Name(id="unique_name_0", ctx=Store()),
            value=SetComp(
                elt=Constant(value=0),
                generators=[
                    comprehension(
                        target=Starred(
                            value=Name(id="unique_name_1", ctx=Store()), ctx=Store()
                        ),
                        iter=Tuple(ctx=Load()),
                        is_async=0,
                    )
                ],
            ),
        )
    ]
)

# version: 3.14.3
# seed = 3570950800
#
# Source:
# type unique_name_0 = {0 for *unique_name_1 in ()}
#
#
# Error:
#     SyntaxError('starred assignment target must be in a list or tuple', ('<file>', 1, 29, None, 1, 43))
