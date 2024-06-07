from ast import Attribute
from ast import Constant
from ast import Load
from ast import Match
from ast import match_case
from ast import MatchValue
from ast import Module
from ast import Name
from ast import Pass

tree = Module(
    body=[
        Match(
            subject=Name(id="name_3", ctx=Load()),
            cases=[
                match_case(
                    pattern=MatchValue(
                        value=Attribute(
                            value=Constant(value=0), attr="name_1", ctx=Load()
                        )
                    ),
                    body=[Pass()],
                )
            ],
        )
    ]
)

# version: 3.13.0b1
# seed = 1710609
#
# Source:
# match name_3:
#     case 0 .name_1:
#         pass
#
#
# Error:
#     SyntaxError('invalid syntax', ('<file>', 2, 12, '    case 0 .name_1:\n', 2, 13))
