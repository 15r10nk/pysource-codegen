from ast import Break
from ast import ExceptHandler
from ast import For
from ast import Load
from ast import Module
from ast import Name
from ast import Pass
from ast import Store
from ast import TryStar

tree = Module(
    body=[
        For(
            target=Name(id="name_1", ctx=Store()),
            iter=Name(id="something", ctx=Load()),
            body=[
                TryStar(
                    body=[Pass()],
                    handlers=[
                        ExceptHandler(
                            type=Name(id="name_4", ctx=Load()), body=[Break()]
                        )
                    ],
                    orelse=[],
                    finalbody=[],
                )
            ],
            orelse=[],
        )
    ],
    type_ignores=[],
)

# version: 3.12.0
#
# Source:
# for name_1 in something:
#     try:
#         pass
#     except* name_4:
#         break
#
#
# Error:
#     SyntaxError("'break', 'continue' and 'return' cannot appear in an except* block", ('<file>', 5, 9, None, 5, 14))
