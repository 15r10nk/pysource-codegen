from ast import Assign
from ast import comprehension
from ast import List
from ast import Load
from ast import Module
from ast import Name
from ast import SetComp
from ast import Starred
from ast import Store

tree = Module(
    body=[
        Assign(
            targets=[
                List(
                    elts=[
                        Starred(
                            value=SetComp(
                                elt=Name(id="name_0", ctx=Load()),
                                generators=[
                                    comprehension(
                                        target=Name(id="name_5", ctx=Store()),
                                        iter=Name(id="name_5", ctx=Load()),
                                        ifs=[],
                                        is_async=0,
                                    )
                                ],
                            ),
                            ctx=Store(),
                        )
                    ],
                    ctx=Store(),
                )
            ],
            value=Name(id="name_0", ctx=Load()),
        )
    ],
    type_ignores=[],
)

# version: 3.12.0
#
# Source:
# [*{name_0 for name_5 in name_5}] = name_0
#
#
# Error:
#     SyntaxError('cannot assign to set comprehension', ('<file>', 1, 3, '[*{name_0 for name_5 in name_5}] = name_0\n', 1, 32))
