from ast import ClassDef
from ast import Constant
from ast import Module
from ast import Name
from ast import NamedExpr
from ast import Pass
from ast import Store
from ast import TypeVar

tree = Module(
    body=[
        ClassDef(
            name="name_2",
            body=[Pass()],
            type_params=[
                TypeVar(
                    name="name_5",
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
# seed = 9482560944
#
# Source:
# class name_2[name_5 = (unique_name_0 := 0)]:
#     pass
#
#
# Error:
#     SyntaxError('named expression cannot be used within a TypeVar default')
