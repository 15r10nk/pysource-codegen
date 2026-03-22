from ast import arguments
from ast import AsyncFunctionDef
from ast import Await
from ast import ClassDef
from ast import Constant
from ast import Module
from ast import ParamSpec
from ast import Pass

tree = Module(
    body=[
        AsyncFunctionDef(
            name="name_3",
            args=arguments(),
            body=[
                ClassDef(
                    name="name_0",
                    bases=[Await(value=Constant(value=0))],
                    body=[Pass()],
                    type_params=[ParamSpec(name="name_5")],
                )
            ],
        )
    ]
)

# version: 3.14.3
# seed = 8470118334
#
# Source:
# async def name_3():
#
#     class name_0[**name_5](await 0):
#         pass
#
#
# Error:
#     SyntaxError('await expression cannot be used within the definition of a generic')
