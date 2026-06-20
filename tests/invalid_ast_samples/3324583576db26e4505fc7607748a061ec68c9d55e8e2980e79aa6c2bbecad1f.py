# pysource-codegen thinks that the this ast is valid python code, but this is not the case:
from ast import Constant
from ast import Load
from ast import Match
from ast import match_case
from ast import MatchClass
from ast import MatchOr
from ast import MatchSequence
from ast import MatchValue
from ast import Module
from ast import Name
from ast import Pass
tree = Module(
  body=[
    Match(
      subject=Constant(value=0),
      cases=[
        match_case(
          pattern=MatchClass(
            cls=Name(id='unique_name_0', ctx=Load()),
            patterns=[
              MatchOr(
                patterns=[
                  MatchClass(
                    cls=Name(id='unique_name_1', ctx=Load()),
                    patterns=[],
                    kwd_attrs=[],
                    kwd_patterns=[]),
                  MatchClass(
                    cls=Name(id='unique_name_2', ctx=Load()),
                    patterns=[],
                    kwd_attrs=[],
                    kwd_patterns=[]),
                  MatchClass(
                    cls=Name(id='unique_name_3', ctx=Load()),
                    patterns=[],
                    kwd_attrs=[],
                    kwd_patterns=[]),
                  MatchValue(
                    value=Constant(value='xt')),
                  MatchValue(
                    value=Constant(value='some const text'))])],
            kwd_attrs=[
              'name_3'],
            kwd_patterns=[
              MatchSequence(patterns=[])]),
          body=[
            Pass()])])],
  type_ignores=[])

# version: 3.12.12
# seed = 6116472296
#
# Source:
# match 0:
#     case unique_name_0(
#         unique_name_1() | unique_name_2() | unique_name_3() | 'xt' | 'some const text',
#     , name_3=[]):
#         pass
#
#
