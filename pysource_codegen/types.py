from dataclasses import dataclass


@dataclass
class NodeType:
    fields: dict
    ast_type: type


@dataclass
class BuiltinNodeType:
    kind: str


@dataclass
class UnionNodeType:
    options: list
