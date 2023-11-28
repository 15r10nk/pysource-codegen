from ast import Match
from ast import Module
from ast import Name
from ast import Store

tree = Module(
    body=[Match(subject=Name(id="name_5", ctx=Store()), cases=[])], type_ignores=[]
)

# version: 3.10.8
# seed = 4737038
#
# Source:
# match name_5:
#
#
# Error:
#     IndentationError("expected an indented block after 'match' statement on line 1", ('<file>', 1, 14, 'match name_5:\n', 1, -1))
