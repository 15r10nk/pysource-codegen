from ast import Attribute
from ast import Constant
from ast import Load
from ast import Match
from ast import match_case
from ast import MatchAs
from ast import MatchOr
from ast import MatchValue
from ast import Module
from ast import Name
from ast import Pass

tree = Module(
    body=[
        Match(
            subject=Name(id="name_4", ctx=Load()),
            cases=[
                match_case(
                    pattern=MatchOr(
                        patterns=[
                            MatchValue(value=Constant(value=b"")),
                            MatchAs(
                                pattern=MatchValue(
                                    value=Attribute(
                                        value=Name(id="name_5", ctx=Load()),
                                        attr="name_5",
                                        ctx=Load(),
                                    )
                                )
                            ),
                        ]
                    ),
                    body=[Pass()],
                )
            ],
        )
    ],
    type_ignores=[],
)

# version: 3.12.0
# seed = 3572769
#
# Source:
# match name_4:
#     case b'' | _:
#         pass
#
#
# Error:
#     ValueError('MatchAs must specify a target name if a pattern is given')
