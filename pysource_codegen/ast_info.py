from __future__ import annotations

import ast
import inspect
import re
import sys

from .types import BuiltinNodeType
from .types import NodeType
from .types import UnionNodeType


type_infos: dict[str, NodeType | BuiltinNodeType | UnionNodeType] = {}


def get_info(name):
    if name in type_infos:
        return type_infos[name]
    elif name in ("identifier", "int", "string", "constant"):
        type_infos[name] = BuiltinNodeType(name)

    else:
        doc = inspect.getdoc(getattr(ast, name)) or ""
        doc = doc.replace("\n", " ")

        if doc:
            m = re.fullmatch(r"(\w*)", doc)
            if m:
                nt = NodeType(fields={}, ast_type=getattr(ast, name))
                name = m.group(1)
                type_infos[name] = nt
            else:
                m = re.fullmatch(r"(\w*)\((.*)\)", doc)
                if m:
                    nt = NodeType(fields={}, ast_type=getattr(ast, name))
                    name = m.group(1)
                    type_infos[name] = nt
                    for string_field in m.group(2).split(","):
                        field_type, field_name = string_field.split()
                        quantity = ""
                        while (last := field_type[-1]) in "*?":
                            quantity = last + quantity
                            field_type = field_type[:-1]

                        nt.fields[field_name] = (field_type, quantity)
                        get_info(field_type)
                elif doc.startswith(f"{name} = "):
                    doc = doc.split(" = ", 1)[1]
                    nt = UnionNodeType(options=[])
                    type_infos[name] = nt
                    nt.options = [d.split("(")[0] for d in doc.split(" | ")]
                    for o in nt.options:
                        get_info(o)

                else:
                    assert False, "can not parse:" + doc
        else:
            assert False, "no doc for " + name

    return type_infos[name]


if sys.version_info < (3, 9):
    from .static_type_info import type_infos  # type: ignore
