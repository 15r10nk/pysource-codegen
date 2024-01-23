from ast import arguments
from ast import ClassDef
from ast import Lambda
from ast import Load
from ast import Module
from ast import Name
from ast import Store
from ast import TypeAlias

tree = Module(
    body=[
        ClassDef(
            name="name_4",
            bases=[],
            keywords=[],
            body=[
                TypeAlias(
                    name=Name(id="name_4", ctx=Store()),
                    type_params=[],
                    value=Lambda(
                        args=arguments(
                            posonlyargs=[],
                            args=[],
                            kwonlyargs=[],
                            kw_defaults=[],
                            defaults=[],
                        ),
                        body=Name(id="name_3", ctx=Load()),
                    ),
                )
            ],
            decorator_list=[],
            type_params=[],
        )
    ],
    type_ignores=[],
)

# version: 3.12.0
# seed = 6421668
#
# Source:
# class name_4:
#     type name_4 = lambda: name_3
#
#
# Error:
#     SyntaxError('Cannot use lambda in annotation scope within class scope')
