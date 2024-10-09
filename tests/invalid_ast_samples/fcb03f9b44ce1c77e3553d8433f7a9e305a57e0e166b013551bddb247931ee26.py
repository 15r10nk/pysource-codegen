from ast import BoolOp
from ast import Load
from ast import Module
from ast import Name
from ast import Or
from ast import ParamSpec
from ast import Store
from ast import TypeAlias
from ast import TypeVarTuple

tree = Module(
    body=[
        TypeAlias(
            name=Name(id="name_1", ctx=Store()),
            type_params=[
                TypeVarTuple(
                    name="name_4", default_value=Name(id="name_1", ctx=Load())
                ),
                ParamSpec(name="name_1"),
            ],
            value=BoolOp(
                op=Or(),
                values=[Name(id="name_5", ctx=Load()), Name(id="name_5", ctx=Load())],
            ),
        )
    ]
)

# version: 3.13.0b1
# seed = 4451400
#
# Source:
# type name_1[*name_4 = name_1, **name_1] = name_5 or name_5
#
#
# Error:
#     SyntaxError("non-default type parameter 'name_1' follows default type parameter", ('<file>', 1, 31, None, 1, 39))
