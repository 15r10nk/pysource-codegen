import ast
from dataclasses import dataclass
from typing import Dict
from typing import List
from typing import Tuple
from typing import Type
from typing import Union

from typing_extensions import Literal  # noqa


@dataclass
class NodeType:
    fields: Dict[str, Tuple[str, Union[Literal["?"], Literal["*"], Literal[""]]]]
    ast_type: Type[ast.AST]


@dataclass
class BuiltinNodeType:
    kind: Union[
        Literal["identifier"], Literal["int"], Literal["string"], Literal["constant"]
    ]


@dataclass
class UnionNodeType:
    options: List[str]
