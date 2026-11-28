from ast import Constant
from ast import Load
from ast import Match
from ast import match_case
from ast import MatchAs
from ast import MatchMapping
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
          pattern=MatchMapping(
            keys=[
              Constant(
                value='a',
                kind=None
              )
            ],
            patterns=[
              MatchAs(
                pattern=None,
                name='x'
              )
            ],
            rest='x'
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
