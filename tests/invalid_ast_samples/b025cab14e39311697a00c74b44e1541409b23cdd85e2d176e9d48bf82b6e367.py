from ast import arguments
from ast import ClassDef
from ast import comprehension
from ast import Constant
from ast import DictComp
from ast import FunctionDef
from ast import Module
from ast import Name
from ast import NamedExpr
from ast import Pass
from ast import Store

tree = Module(
    body=[
        ClassDef(
            name="name_0",
            body=[
                FunctionDef(
                    name="name_0",
                    args=arguments(),
                    body=[Pass()],
                    decorator_list=[
                        DictComp(
                            key=Constant(value=0),
                            value=NamedExpr(
                                target=Name(id="unique_name_0", ctx=Store()),
                                value=Constant(value=0),
                            ),
                            generators=[
                                comprehension(
                                    target=Name(id="unique_name_1", ctx=Store()),
                                    iter=Constant(value=0),
                                    is_async=0,
                                )
                            ],
                        )
                    ],
                )
            ],
        )
    ]
)

# version: 3.14.3
# seed = 3037423696
#
# Source:
# class name_0:
#
#     @{0: (unique_name_0 := 0) for unique_name_1 in 0}
#     def name_0():
#         pass
#
#
# Error:
#     SyntaxError('assignment expression within a comprehension cannot be used in a class body')
