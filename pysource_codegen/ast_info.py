from __future__ import annotations

import ast
import inspect
import re
import sys
from typing import cast
from typing import Literal

from .types import BuiltinNodeType
from .types import NodeType
from .types import UnionNodeType

# Narrow, reusable aliases for literals used in the type model
BuiltinKind = Literal["identifier", "int", "string", "constant"]
FieldQuantity = Literal["?", "*", ""]


type_infos: dict[str, NodeType | BuiltinNodeType | UnionNodeType] = {}


def get_info(name: str) -> NodeType | BuiltinNodeType | UnionNodeType:
    if name in type_infos:
        return type_infos[name]

    elif name in ("identifier", "int", "string", "constant"):
        # Narrow the kind to the expected Literal type for safer typing.
        kind = cast(BuiltinKind, name)
        type_infos[name] = BuiltinNodeType(kind=kind)

    else:
        doc = inspect.getdoc(getattr(ast, name)) or ""
        doc = doc.replace("\n", " ")

        if doc:
            m = re.fullmatch(r"(\w*)", doc)
            if m:
                nt_node: NodeType = NodeType(fields={}, ast_type=getattr(ast, name))
                type_name = m.group(1)
                type_infos[type_name] = nt_node
            else:
                m = re.fullmatch(r"(\w*)\((.*)\)", doc)
                if m:
                    nt_node = NodeType(fields={}, ast_type=getattr(ast, name))
                    type_name = m.group(1)
                    type_infos[type_name] = nt_node
                    for string_field in m.group(2).split(","):
                        field_type, field_name = string_field.split()
                        quantity = ""
                        while (last := field_type[-1]) in "*?":
                            quantity = last + quantity
                            field_type = field_type[:-1]

                        nt_node.fields[field_name] = (
                            field_type,
                            cast(FieldQuantity, quantity),
                        )
                        get_info(field_type)
                elif doc.startswith(f"{name} = "):
                    doc = doc.split(" = ", 1)[1]
                    nt_union = UnionNodeType(options=[])
                    type_infos[name] = nt_union
                    nt_union.options = [d.split("(")[0] for d in doc.split(" | ")]
                    for o in nt_union.options:
                        get_info(o)

                else:
                    assert False, "can not parse:" + doc
        else:
            assert False, "no doc for " + name

    return type_infos[name]


if sys.version_info < (3, 9):
    from .static_type_info import type_infos  # type: ignore
