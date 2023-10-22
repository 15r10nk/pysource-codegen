from ast import Break
from ast import ExceptHandler
from ast import For
from ast import Load
from ast import Module
from ast import Name
from ast import Pass
from ast import TryStar

tree = Module(
    body=[
        For(
            target=Name(id="something", ctx=Load()),
            iter=Name(id="name_2", ctx=Load()),
            body=[
                TryStar(
                    body=[Pass()],
                    handlers=[
                        ExceptHandler(
                            type=Name(id="name_5", ctx=Load()), body=[Break()]
                        )
                    ],
                    orelse=[],
                    finalbody=[],
                )
            ],
            orelse=[],
            type_comment="",
        )
    ],
    type_ignores=[],
)

# Source:
# for something in name_2: # type:
#     try:
#         pass
#     except* name_5:
#         break
# Error:
#     SyntaxError("'break', 'continue' and 'return' cannot appear in an except* block", ('<file>', 5, 9, None, 5, 14))
