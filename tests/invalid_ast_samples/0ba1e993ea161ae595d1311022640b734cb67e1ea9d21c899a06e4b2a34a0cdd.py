# The checker accepts this generated AST, but it fails compilation or AST round-trip.
from ast import arg
from ast import arguments
from ast import Attribute
from ast import comprehension
from ast import Constant
from ast import GeneratorExp
from ast import Lambda
from ast import List
from ast import Load
from ast import Module
from ast import Name
from ast import NamedExpr
from ast import Store
from ast import TypeAlias
tree = Module(
  body=[
    TypeAlias(
      name=Name(
        id='unique_name_0',
        ctx=Store()
      ),
      type_params=[],
      value=GeneratorExp(
        elt=Lambda(
          args=arguments(
            posonlyargs=[],
            args=[],
            vararg=None,
            kwonlyargs=[
              arg(
                arg='name_2',
                annotation=None,
                type_comment=None
              )
            ],
            kw_defaults=[
              NamedExpr(
                target=Name(
                  id='unique_name_1',
                  ctx=Store()
                ),
                value=Constant(
                  value=0,
                  kind=None
                )
              )
            ],
            kwarg=None,
            defaults=[]
          ),
          body=Constant(
            value=0,
            kind=None
          )
        ),
        generators=[
          comprehension(
            target=Attribute(
              value=Constant(
                value=0,
                kind=None
              ),
              attr='name_0',
              ctx=Store()
            ),
            iter=List(
              elts=[],
              ctx=Load()
            ),
            ifs=[],
            is_async=1
          )
        ]
      )
    )
  ],
  type_ignores=[]
)

# version: 3.15.2
# seed = 6305851986
#
# checker accepts: True
# valid_python: False
#
# SyntaxError: assignment expression within a comprehension cannot be used in a type alias (<source>, line 1)Source:
# type unique_name_0 = (lambda *, name_2=(unique_name_1 := 0): 0 async for (0).name_0 in [])
#
#
