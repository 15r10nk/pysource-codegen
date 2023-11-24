from ast import arguments
from ast import BoolOp
from ast import FunctionDef
from ast import Global
from ast import Load
from ast import Module
from ast import Name
from ast import Or
from ast import Pass

tree = Module(
    body=[
        FunctionDef(
            name="name_3",
            args=arguments(
                posonlyargs=[], args=[], kwonlyargs=[], kw_defaults=[], defaults=[]
            ),
            body=[Pass()],
            decorator_list=[],
            returns=BoolOp(
                op=Or(),
                values=[Name(id="name_0", ctx=Load()), Name(id="name_5", ctx=Load())],
            ),
        ),
        Global(names=["name_5"]),
    ],
    type_ignores=[],
)

# version: 3.9.15
#
# Source:
# def name_3() -> name_0 or name_5:
#     pass
# global name_5
#
#
# Error:
#     SyntaxError("name 'name_5' is used prior to global declaration")
# seed = 4445204
