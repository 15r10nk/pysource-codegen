from ast import Dict
from ast import Load
from ast import Module
from ast import Name
from ast import TypeAlias

tree = Module(
    body=[
        TypeAlias(
            name=Name(id="name_4", ctx=Load()),
            type_params=[],
            value=Dict(keys=[], values=[]),
        )
    ],
    type_ignores=[],
)

# version: 3.12.0
# seed = 4378073
#
# Source:
# type name_4 = {}
#
#
# Error:
#     ValueError('expression must have Store context but has Load instead')
