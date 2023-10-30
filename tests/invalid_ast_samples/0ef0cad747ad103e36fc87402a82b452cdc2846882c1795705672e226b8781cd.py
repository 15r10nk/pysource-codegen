from ast import And
from ast import arg
from ast import arguments
from ast import AsyncFor
from ast import AsyncFunctionDef
from ast import BinOp
from ast import BoolOp
from ast import FloorDiv
from ast import FunctionDef
from ast import Lambda
from ast import Load
from ast import Module
from ast import Name
from ast import Pass
from ast import Store

tree = Module(
    body=[
        AsyncFunctionDef(
            name="name_4",
            args=arguments(
                posonlyargs=[],
                args=[],
                kwonlyargs=[],
                kw_defaults=[
                    BoolOp(
                        op=And(),
                        values=[
                            Name(id="name_5", ctx=Load()),
                            Name(id="name_3", ctx=Load()),
                            Name(id="name_1", ctx=Load()),
                        ],
                    ),
                    BinOp(
                        left=Name(id="name_5", ctx=Load()),
                        op=FloorDiv(),
                        right=Name(id="name_4", ctx=Load()),
                    ),
                    BoolOp(
                        op=And(),
                        values=[
                            Name(id="name_3", ctx=Load()),
                            Name(id="name_3", ctx=Load()),
                            Name(id="name_2", ctx=Load()),
                        ],
                    ),
                    Lambda(
                        args=arguments(
                            posonlyargs=[arg(arg="name_5")],
                            args=[arg(arg="name_3", type_comment="some text")],
                            vararg=arg(arg="name_2"),
                            kwonlyargs=[arg(arg="name_4", type_comment="")],
                            kw_defaults=[Name(id="name_1", ctx=Load())],
                            kwarg=arg(arg="name_0", type_comment="some text"),
                            defaults=[Name(id="name_4", ctx=Load())],
                        ),
                        body=Name(id="name_2", ctx=Load()),
                    ),
                ],
                defaults=[],
            ),
            body=[
                FunctionDef(
                    name="name_1",
                    args=arguments(
                        posonlyargs=[],
                        args=[],
                        kwonlyargs=[],
                        kw_defaults=[Name(id="name_0", ctx=Load())],
                        defaults=[],
                    ),
                    body=[
                        AsyncFor(
                            target=Name(id="name_0", ctx=Store()),
                            iter=Name(id="name_4", ctx=Load()),
                            body=[Pass()],
                            orelse=[],
                            type_comment="some text",
                        )
                    ],
                    decorator_list=[],
                    type_params=[],
                )
            ],
            decorator_list=[],
            type_params=[],
        )
    ],
    type_ignores=[],
)

# version: 3.12.0
#
# Source:
# async def name_4():
#
#     def name_1():
#         async for name_0 in name_4: # type: some text
#             pass
#
#
# Error:
#     SyntaxError("'async for' outside async function", ('<file>', 4, 9, None, 5, 17))
