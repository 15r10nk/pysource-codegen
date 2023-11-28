import ast
import sys
from typing import Dict


def only_if(condition: bool, **kwargs) -> Dict:
    return kwargs if condition else {}


def ast_dump(node):
    return ast.dump(node, **only_if(sys.version_info >= (3, 9), indent=2))
