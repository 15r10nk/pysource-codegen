from ast import arg
from ast import arguments
from ast import Attribute
from ast import comprehension
from ast import Constant
from ast import FunctionDef
from ast import GeneratorExp
from ast import JoinedStr
from ast import Lambda
from ast import Load
from ast import Module
from ast import Name
from ast import Pass
from ast import Set
from ast import Store

tree = Module(
    body=[
        FunctionDef(
            name="name_4",
            args=arguments(
                posonlyargs=[],
                args=[],
                kwonlyargs=[
                    arg(
                        arg="name_2",
                        annotation=GeneratorExp(
                            elt=Lambda(
                                args=arguments(
                                    posonlyargs=[arg(arg="name_5")],
                                    args=[arg(arg="name_3", type_comment="some text")],
                                    kwonlyargs=[arg(arg="name_1")],
                                    kw_defaults=[Name(id="name_1", ctx=Load())],
                                    defaults=[Name(id="name_5", ctx=Load())],
                                ),
                                body=Name(id="name_0", ctx=Load()),
                            ),
                            generators=[
                                comprehension(
                                    target=Name(id="name_3", ctx=Store()),
                                    iter=Name(id="name_0", ctx=Load()),
                                    ifs=[
                                        Name(id="name_0", ctx=Load()),
                                        Name(id="name_2", ctx=Load()),
                                        Name(id="name_4", ctx=Load()),
                                        Name(id="name_0", ctx=Load()),
                                        Name(id="name_3", ctx=Load()),
                                    ],
                                    is_async=4,
                                ),
                                comprehension(
                                    target=Name(id="name_0", ctx=Store()),
                                    iter=Name(id="name_5", ctx=Load()),
                                    ifs=[
                                        Name(id="name_0", ctx=Load()),
                                        Name(id="name_5", ctx=Load()),
                                    ],
                                    is_async=4,
                                ),
                                comprehension(
                                    target=Name(id="name_2", ctx=Store()),
                                    iter=Name(id="name_2", ctx=Load()),
                                    ifs=[Name(id="name_2", ctx=Load())],
                                    is_async=1,
                                ),
                                comprehension(
                                    target=Name(id="name_1", ctx=Store()),
                                    iter=Name(id="name_5", ctx=Load()),
                                    ifs=[
                                        Name(id="name_3", ctx=Load()),
                                        Name(id="name_4", ctx=Load()),
                                        Name(id="name_2", ctx=Load()),
                                        Name(id="name_2", ctx=Load()),
                                        Name(id="name_1", ctx=Load()),
                                    ],
                                    is_async=0,
                                ),
                            ],
                        ),
                        type_comment="",
                    )
                ],
                kw_defaults=[],
                defaults=[
                    JoinedStr(values=[Constant(value="")]),
                    Attribute(
                        value=Set(elts=[Name(id="name_1", ctx=Load())]),
                        attr="name_2",
                        ctx=Load(),
                    ),
                ],
            ),
            body=[Pass()],
            decorator_list=[],
        )
    ],
    type_ignores=[],
)

# version: 3.9.15
#
# Source:
# def name_4(*):
#     pass
#
#
# Error:
#     SyntaxError('named arguments must follow bare *', ('<file>', 1, 13, 'def name_4(*):\n'))
