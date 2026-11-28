from ast import Load
from ast import Match
from ast import match_case
from ast import MatchAs
from ast import MatchClass
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
          pattern=MatchClass(
            cls=Name(
              id='C',
              ctx=Load()
            ),
            patterns=[
              MatchAs(
                pattern=None,
                name='x'
              )
            ],
            kwd_attrs=[
              'value'
            ],
            kwd_patterns=[
              MatchAs(
                pattern=None,
                name='x'
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
