from __future__ import annotations

import ast
import sys
import traceback
from copy import deepcopy

from ._codegen_rules import equal_ast
from ._codegen_rules import fix
from ._codegen_rules import fix_result
from ._codegen_rules import Invalid
from ._codegen_rules import min_attr_length
from ._codegen_rules import none_allowed
from ._codegen_rules import probability
from ._codegen_rules import probability_try
from ._codegen_rules import same_length
from ._codegen_rules import use
from ._utils import ast_dump
from ._utils import unparse
from .ast_info import get_info
from .types import BuiltinNodeType
from .types import NodeType
from .types import UnionNodeType


def is_valid_ast(tree, print=lambda *l: None) -> bool:
    def is_valid(node: ast.AST, parents):
        type_name = node.__class__.__name__
        if (
            isinstance(node, (ast.AST))
            and parents
            and probability(
                parents,
                type_name,
            )
            == 0
        ):
            print("invalid node with:")
            print("parents:", parents)
            print("node:", node)

            try:
                probability_try(
                    parents,
                    node.__class__.__name__,
                )
            except Invalid:
                frame = traceback.extract_tb(sys.exc_info()[2])[1]
                print("file:", f"{frame.filename}:{frame.lineno}")

            return False

        if type_name in same_length:
            attrs = same_length[type_name]
            if len({len(v) for k, v in ast.iter_fields(node) if k in attrs}) != 1:
                return False

        if isinstance(node, (ast.AST)):
            info = get_info(type_name)
            assert isinstance(info, NodeType)

            for attr_name, value in ast.iter_fields(node):
                assert attr_name in info.fields, f"{attr_name} missing in {info}"
                attr_info = info.fields[attr_name]
                if attr_info[1] == "":
                    value_info = get_info(attr_info[0])
                    if isinstance(value_info, UnionNodeType):
                        if type(value).__name__ not in value_info.options:
                            print(
                                f"{type(node).__name__}.{attr_name} {value} is not one type of {value_info.options}"
                            )
                            print("parents are:", parents)
                            return False

                if isinstance(value, list) and len(value) < min_attr_length(
                    type_name, attr_name
                ):
                    print("invalid arg length", type_name, attr_name)
                    return False

                if isinstance(value, list) != ("*" in info.fields[attr_name][1]):
                    print(f"no list (info {info.fields[attr_name]})")
                    return False
                if value is None:
                    if not (
                        (
                            info.fields[attr_name][1] == "?"
                            and none_allowed(parents + [(type_name, attr_name)])
                        )
                        or info.fields[attr_name][0] == "constant"
                    ):
                        print("none not allowed", parents, type_name, attr_name)
                        return False

            for field in node._fields:
                value = getattr(node, field)
                if isinstance(value, list):
                    if not all(
                        is_valid(e, parents + [(type_name, field)]) for e in value
                    ):
                        return False
                else:
                    if not is_valid(value, parents + [(type_name, field)]):
                        return False
        return True

    if not is_valid(tree, []):
        return False

    def fix_tree(node: ast.AST, parents):
        for field in node._fields:
            value = getattr(node, field)
            if isinstance(value, ast.AST):
                setattr(
                    node,
                    field,
                    fix_tree(value, parents + [(node.__class__.__name__, field)]),
                )
            if isinstance(value, list):
                setattr(
                    node,
                    field,
                    [
                        (
                            fix_tree(v, parents + [(node.__class__.__name__, field)])
                            if isinstance(v, ast.AST)
                            else v
                        )
                        for v in value
                    ],
                )

        return fix(node, parents)

    def check_if_changed(tree, tree_copy, operation):
        result = equal_ast(tree_copy, tree, print)

        if sys.version_info >= (3, 9) and not result:
            dump = ast_dump(tree).splitlines()
            dump_copy = ast_dump(tree_copy).splitlines()
            import difflib

            print(f"ast was changed while running {operation}:")

            print(
                "\n".join(
                    difflib.unified_diff(dump, dump_copy, "original", "fixed", n=10)
                )
            )
        return result

    tree_copy = deepcopy(tree)

    tree_copy = fix_tree(tree_copy, [])
    if not check_if_changed(tree, tree_copy, "fix_tree"):
        return False

    tree_copy = fix_result(tree_copy)
    if not check_if_changed(tree, tree_copy, "fix_result"):
        return False

    return True


class AstGenerator:
    def __init__(self, seed, node_limit, depth_limit):
        self.rand = random.Random(seed)
        self.nodes = 0
        self.node_limit = node_limit
        self.depth_limit = depth_limit

    def cnd(self):
        return self.rand.choice([True, False])

    def generate(self, name: str, parents=(), depth=0):
        result = self.generate_impl(name, parents, depth)
        result = fix_result(result)
        return result

    def generate_impl(self, name: str, parents=(), depth=0):
        depth += 1
        self.nodes += 1

        if depth > 100:
            exit()

        stop = depth > self.depth_limit or self.nodes > self.node_limit

        info = get_info(name)

        if isinstance(info, NodeType):
            ranges = {}

            def attr_length(child, attr_name):
                if name == "Module":
                    return 20

                if name in same_length:
                    attrs = same_length[name]
                    if attr_name in attrs[1:]:
                        return attr_length(child, attrs[0])

                if child == "arguments" and attr_name == "defaults":
                    min = 0
                    max = attr_length(child, "posonlyargs") + attr_length(child, "args")
                    ranges[attr_name] = self.rand.randint(min, max)

                elif attr_name not in ranges:
                    min = min_attr_length(child, attr_name)

                    max = min if stop else min + 1 if depth > 10 else min + 5
                    ranges[attr_name] = self.rand.randint(min, max)

                return ranges[attr_name]

            def child_node(n, t, q, parents):
                if q == "":
                    return self.generate_impl(t, parents, depth)
                elif q == "*":
                    return [
                        self.generate_impl(t, parents, depth)
                        for _ in range(attr_length(parents[-1][0], n))
                    ]
                elif q == "?":
                    return (
                        self.generate_impl(t, parents, depth)
                        if not none_allowed(parents) or self.cnd()
                        else None
                    )
                elif q == "?*":
                    return [
                        (
                            self.generate_impl(t, parents, depth)
                            if not none_allowed(parents) or self.cnd()
                            else None
                        )
                        for _ in range(attr_length(parents[-1][0], n))
                    ]

                else:
                    assert False, q

            attributes = {
                n: child_node(n, t, q, [*parents, (name, n)])
                for n, (t, q) in info.fields.items()
            }

            result = info.ast_type(**attributes)
            result = fix(result, parents)
            return result

        if isinstance(info, UnionNodeType):
            options_list = [
                (option, probability(parents, option)) for option in info.options
            ]

            invalid_option = [
                option for (option, prop) in options_list if prop == 0 and not use()
            ]

            assert len(invalid_option) in (0, 1), invalid_option

            if len(invalid_option) == 1:
                return self.generate_impl(invalid_option[0])

            options = dict(options_list)
            if stop:
                for final in ("Name", "MatchValue", "Pass"):
                    if options.get(final, 0) != 0:
                        options = {final: 1}
                        break

            if sum(options.values()) == 0:
                # TODO: better handling of `type?`
                return None

            return self.generate_impl(
                self.rand.choices(*zip(*options.items()))[0], parents, depth
            )
        if isinstance(info, BuiltinNodeType):
            if info.kind == "identifier":
                return f"name_{self.rand.randint(0,5)}"
            elif info.kind == "int":
                return self.rand.randint(0, 5)
            elif info.kind == "string":
                return self.rand.choice(["some text", ""])
            elif info.kind == "constant":
                return self.rand.choice(
                    [
                        None,
                        b"some bytes",
                        "some const text",
                        b"",
                        "",
                        "'\"'''\"\"\"{}\\",
                        b"'\"'''\"\"\"{}\\",
                        b"\xef\xbb\xbf",  # utf-8
                        b"\xff\xfe\0\0",  # utf-32
                        b"\0\0\xfe\xff",  # utf-32be
                        b"\xff\xfe",  # utf-16
                        b"\xfe\xff",  # utf-16be
                        self.rand.randint(0, 20),
                        self.rand.uniform(0, 20),
                        True,
                        False,
                    ]
                )

            else:
                assert False, "unknown kind: " + info.kind

        assert False


import warnings


def check(tree):
    for node in ast.walk(tree):
        if isinstance(node, ast.arguments):
            assert len(node.posonlyargs) + len(node.args) >= len(
                node.defaults
            ), ast_dump(node)
            assert len(node.kwonlyargs) == len(node.kw_defaults)


def generate_ast(
    seed: int,
    *,
    node_limit: int = 10000000,
    depth_limit: int = 8,
    root_node: str = "Module",
) -> ast.AST:
    generator = AstGenerator(seed, depth_limit=depth_limit, node_limit=node_limit)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", SyntaxWarning)
        tree = generator.generate(root_node)
        check(tree)

    ast.fix_missing_locations(tree)
    return tree


def generate(
    seed: int,
    *,
    node_limit: int = 10000000,
    depth_limit: int = 8,
    root_node: str = "Module",
) -> str:
    tree = generate_ast(
        seed, node_limit=node_limit, depth_limit=depth_limit, root_node=root_node
    )
    return unparse(tree)
