from ast import AnnAssign
from ast import comprehension
from ast import Constant
from ast import Module
from ast import Name
from ast import SetComp
from ast import Starred
from ast import Store

tree = Module(
    body=[
        AnnAssign(
            target=Name(id="unique_name_0", ctx=Store()),
            annotation=SetComp(
                elt=Constant(value=0),
                generators=[
                    comprehension(
                        target=Starred(
                            value=Name(id="unique_name_1", ctx=Store()), ctx=Store()
                        ),
                        iter=Constant(value=b""),
                        is_async=0,
                    )
                ],
            ),
            simple=2,
        )
    ]
)

# version: 3.14.3
# seed = 419468654
#
# Source:
# unique_name_0: {0 for *unique_name_1 in b''}
#
#
# Error:
#     SyntaxError('starred assignment target must be in a list or tuple', ('<file>', 1, 23, None, 1, 37))
