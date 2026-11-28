from ast import alias
from ast import ImportFrom
from ast import Module

lazy_import = ImportFrom(
    module="__future__", names=[alias(name="annotations")], level=0
)
lazy_import.is_lazy = 1
tree = Module(body=[lazy_import])

# version: 3.15.1
#
# Source:
# lazy from __future__ import annotations
#
#
# Error:
#     SyntaxError('lazy from __future__ import is not allowed', ('<file>', 1, 1, 'lazy from __future__ import annotations\n', 1, 5))
