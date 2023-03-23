import ast
import inspect
import re

from dataclasses import dataclass, field

import hypothesis.strategies as st
from hypothesis import given, settings, HealthCheck, target

from pprint import pprint

import hypothesis.internal.conjecture.engine as engine

engine.BUFFER_SIZE = 10000000


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


type_infos = {}


def get_info(name):
    if name in type_infos:
        return type_infos[name]
    elif name in ("identifier", "int", "string", "constant"):
        type_infos[name] = BuiltinNodeType(name)

    else:
        doc = inspect.getdoc(getattr(ast, name))
        doc = doc.replace("\n", " ")

        if doc:
            if m := re.fullmatch(r"(\w*)", doc):
                nt = NodeType(fields={}, ast_type=getattr(ast, name))
                name = m.group(1)
                type_infos[name] = nt
            elif m := re.fullmatch(r"(\w*)\((.*)\)", doc):
                nt = NodeType(fields={}, ast_type=getattr(ast, name))
                name = m.group(1)
                type_infos[name] = nt
                for string_field in m.group(2).split(","):
                    field_type, field_name = string_field.split()
                    quantity = ""
                    if (last := field_type[-1]) in "*?":
                        quantity = last
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
            assert False, "no doc"

    return type_infos[name]


get_info("Delete").fields = {"targets": ("_deleteTargets", "*")}
type_infos["_deleteTargets"] = UnionNodeType(options=["Name", "Attribute", "Subscript"])


import random


def propability(parents, child_name):
    if child_name == "Slice":
        if parents[-1] != ("Subscript", "slice") or parents[-2:] != [
            ("Subscript", "slice"),
            ("Tuple", "elts"),
        ]:
            return 0

    if parents[-1][0] == "FormattedValue" and child_name != "Constant":
        return 0

    assign_target = ("Subscript", "Attribute", "Name", "Starred", "List", "Tuple")

    if parents[-1] in [("For", "target"), ("AsyncFor", "target"),("AnnAssign","target")]:
        if child_name not in assign_target:
            return 0


    if child_name == "AsyncFor":
        for parent,_ in reversed(parents):
            if parent == "AsyncFunctionDef":
                break
        else:
            return 0

    return 1


def fix(node):
    if isinstance(node, ast.ImportFrom):
        if node.module == None and (node.level == None or node.level == 0):
            node.level=1

    if isinstance(node, ast.ExceptHandler):
        if node.type is None:
            node.name=None
            
    if isinstance(node,ast.AsyncFunctionDef):
        seen=set()
        for args in (node.args.posonlyargs,node.args.args, node.args.kwonlyargs):
            for i,arg in reversed(list(enumerate(args))):
                if arg.arg in seen:
                    del args[i]
                seen.add(arg.arg)

        if node.args.vararg and  node.args.vararg.arg in seen:
            seen.add(node.args.vararg.arg)
            node.args.vararg=None

        if node.args.kwarg and node.args.kwarg.arg in seen:
            seen.add(node.args.kwarg.arg)
            node.args.kwarg=None


    


class AstGenerator:
    def __init__(self):
        self.rand = random.Random(3)
        self.nodes = 0

    def cnd(self):
        return self.rand.choice([True, False])

    def generate(self, name: str, parents=(), depth=0):
        depth += 1
        self.nodes += 1

        if depth > 100:
            exit()

        stop = depth > 5 or self.nodes > 1000000

        info = get_info(name)

        if name == "JoinedStr":
            return info.ast_type(
                values=[
                    self.rand.choice(
                        [
                            self.generate("FormattedValue", parents, depth),
                            ast.Constant(value="some text"),
                        ]
                    )
                    for _ in range(0, 5)
                ]
            )

        if isinstance(info, NodeType):
            ranges = {}

            def range_for(attr_name):
                if name == "MatchClass" and attr_name == "kwd_patterns":
                    attr_name = "kwd_attrs"

                if name == "MatchMapping" and attr_name == "patterns":
                    attr_name = "keys"

                if attr_name not in ranges:
                    min = 1 if attr_name == "body" else 0
                    max = min if stop else min + 1 if depth > 10 else min + 5
                    max = self.rand.randint(min + 1, max + 1)
                    ranges[attr_name] = range(min, max)

                return ranges[attr_name]

            def child_node(n, t, q, parents):
                if q == "":
                    return self.generate(t, parents, depth)
                elif q == "*":
                    return [self.generate(t, parents, depth) for _ in range_for(n)]
                elif q == "?":
                    return self.generate(t, parents, depth) if self.cnd() else None
                else:
                    assert False

            attributes = {
                n: child_node(n, t, q, [*parents, (name, n)])
                for n, (t, q) in info.fields.items()
            }

            result=info.ast_type(**attributes)
            fix(result)
            return result


        if isinstance(info, UnionNodeType):
            options = info.options
            weights = [propability(parents, option) for option in options]
            if stop:
                for final in ("Name", "MatchValue", "Pass"):
                    if final in options:
                        options = [final]
                        weights = [1]
                        break

            return self.generate(self.rand.choices(options, weights)[0], parents, depth)
        if isinstance(info, BuiltinNodeType):
            if info.kind == "identifier":
                return f"name_{self.rand.randint(0,5)}"
            elif info.kind == "int":
                return self.rand.randint(0, 5)
            elif info.kind == "string":
                return self.rand.choice(["some text", ""])
            elif info.kind == "constant":
                return self.rand.choice(
                    [None, "some const text", "", 1, 0, True, False]
                )

            else:
                assert False, "unknown kind: " + info.kind

        assert False


import tempfile

with tempfile.NamedTemporaryFile("w") as file:

    tree = AstGenerator().generate("Module")
    print(ast.dump(tree, indent=2))
    ast.fix_missing_locations(tree)
    source=ast.unparse(tree)
    print(source)
    file.write(source)
    file.flush()
    compile(ast.unparse(tree), file.name, "exec")
