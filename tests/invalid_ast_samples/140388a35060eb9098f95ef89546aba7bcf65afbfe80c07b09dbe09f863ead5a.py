from ast import Load
from ast import Match
from ast import match_case
from ast import MatchAs
from ast import Module
from ast import Name
from ast import Pass

tree = Module(
  body=[
    Match(
      subject=Name(
        id='subject',
        ctx=Load()
      ),
      cases=[
        match_case(
          pattern=MatchAs(
            pattern=MatchAs(
              pattern=None,
              name='x'
            ),
            name='x'
          ),
          guard=None,
          body=[
            Pass()
          ]
        )
      ]
    )
  ],
  type_ignores=[]
)
