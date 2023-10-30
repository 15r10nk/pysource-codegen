from ast import Attribute
from ast import Constant
from ast import Dict
from ast import JoinedStr
from ast import List
from ast import Load
from ast import Module
from ast import Name
from ast import Set
from ast import Starred
from ast import TypeAlias

tree = Module(
    body=[
        TypeAlias(
            name=None,
            type_params=[],
            value=Dict(
                keys=[
                    Set(
                        elts=[
                            List(elts=[Name(id="name_5", ctx=Load())], ctx=Load()),
                            Starred(value=Name(id="name_1", ctx=Load()), ctx=Load()),
                            List(elts=[Name(id="name_3", ctx=Load())], ctx=Load()),
                            JoinedStr(values=[Constant(value="text")]),
                        ]
                    ),
                    Attribute(
                        value=Set(elts=[Name(id="name_5", ctx=Load())]),
                        attr="name_5",
                        ctx=Load(),
                    ),
                ],
                values=[],
            ),
        )
    ],
    type_ignores=[],
)

# version: 3.12.0
#
#
# Error:
#     AttributeError("'NoneType' object has no attribute '_fields'")
