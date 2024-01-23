from ast import arguments
from ast import comprehension
from ast import DictComp
from ast import FunctionDef
from ast import Global
from ast import Load
from ast import Match
from ast import match_case
from ast import MatchSingleton
from ast import Module
from ast import Name
from ast import NamedExpr
from ast import Store

tree = Module(
    body=[
        FunctionDef(
            name="name_0",
            args=arguments(
                posonlyargs=[], args=[], kwonlyargs=[], kw_defaults=[], defaults=[]
            ),
            body=[
                Match(
                    subject=DictComp(
                        key=Name(id="name_0", ctx=Load()),
                        value=NamedExpr(
                            target=Name(id="name_3", ctx=Load()),
                            value=Name(id="name_3", ctx=Load()),
                        ),
                        generators=[
                            comprehension(
                                target=Name(id="name_4", ctx=Store()),
                                iter=Name(id="name_1", ctx=Load()),
                                ifs=[],
                                is_async=0,
                            )
                        ],
                    ),
                    cases=[
                        match_case(
                            pattern=MatchSingleton(value=19),
                            body=[Global(names=["name_3"])],
                        )
                    ],
                )
            ],
            decorator_list=[],
        )
    ],
    type_ignores=[],
)

# version: 3.11.0
# seed = 8805753
#
# Source:
# def name_0():
#     match {name_0: (name_3 := name_3) for name_4 in name_1}:
#         case 19:
#             global name_3
#
#
# Error:
#     SyntaxError("name 'name_3' is assigned to before global declaration")
