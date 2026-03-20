from ast import arguments
from ast import Constant
from ast import FunctionDef
from ast import Module
from ast import Name
from ast import NamedExpr
from ast import ParamSpec
from ast import Pass
from ast import Store

tree = Module(
    body=[
        FunctionDef(
            name="name_1",
            args=arguments(),
            body=[Pass()],
            type_params=[
                ParamSpec(
                    name="name_4",
                    default_value=NamedExpr(
                        target=Name(id="unique_name_0", ctx=Store()),
                        value=Constant(value=0),
                    ),
                )
            ],
        )
    ]
)

# version: 3.14.3
# seed = 7328965610
#
# Source:
# def name_1[**name_4 = (unique_name_0 := 0)]():
#     pass
#
#
# Error:
#     SyntaxError('named expression cannot be used within a ParamSpec default')
