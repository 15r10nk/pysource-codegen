from ast import Load
from ast import Match
from ast import match_case
from ast import MatchSequence
from ast import MatchStar
from ast import Module
from ast import Name
from ast import Pass

tree = Module(
    body=[Match(
        subject=Name(id="subject", ctx=Load()),
        cases=[match_case(
            pattern=MatchSequence(patterns=[
                MatchStar(name="lost"),
                MatchStar(name=None),
            ]),
            guard=None,
            body=[Pass()],
        )],
    )],
    type_ignores=[],
)
