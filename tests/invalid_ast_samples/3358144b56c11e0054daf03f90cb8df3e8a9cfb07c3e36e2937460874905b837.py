from ast import Load
from ast import Match
from ast import match_case
from ast import MatchAs
from ast import MatchOr
from ast import MatchSequence
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
          pattern=MatchOr(
            patterns=[
              MatchSequence(
                patterns=[
                  MatchAs(
                    pattern=None,
                    name='x'
                  )
                ]
              ),
              MatchSequence(
                patterns=[
                  MatchAs(
                    pattern=None,
                    name='y'
                  )
                ]
              )
            ]
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
