from ast import arguments
from ast import AsyncFunctionDef
from ast import Break
from ast import For
from ast import Module
from ast import Name
from ast import Store

tree = Module(
    body=[
        For(
            target=Name(id="name_4", ctx=Store()),
            iter=Name(id="name_5", ctx=Store()),
            body=[
                AsyncFunctionDef(
                    name="name_5",
                    args=arguments(
                        posonlyargs=[],
                        args=[],
                        kwonlyargs=[],
                        kw_defaults=[],
                        defaults=[],
                    ),
                    body=[Break()],
                    decorator_list=[],
                    type_params=[],
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
# for name_4 in name_5:
#
#     async def name_5():
#         break
#
#
# Error:
#     SyntaxError("'break' outside loop", ('<file>', 4, 9, None, 4, 14))
