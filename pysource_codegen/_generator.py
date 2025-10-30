from __future__ import annotations

import ast
import random
import sys
import traceback
from copy import deepcopy
from dataclasses import dataclass
from typing import Callable
from typing import Sequence
from typing import Union

from ._utils import ast_dump
from ._utils import equal_ast
from .ast_info import get_info
from .types import BuiltinNodeType
from .types import NodeType
from .types import UnionNodeType

# A generated value can be either an AST node or one of the builtin leaf values
GeneratedValue = Union[ast.AST, str, int, float, bytes, bool, None]


class Invalid(Exception):
    pass


class Context:
    pass


@dataclass
class NodeRef:
    parent: NodeRef | None
    parent_attr: str
    parent_attr_index: int | None
    node: ast.AST

    def __getattr__(self, name: str) -> NodeRef | list[NodeRef] | None:
        value = getattr(self.node, name)
        if isinstance(value, list):
            return [NodeRef(self, name, i, n) for i, n in enumerate(value)]
        if value is None:
            return None
        return NodeRef(self, name, None, value)


def parents_of(node: NodeRef | None) -> list[tuple[str, str]]:
    if node is None or node.parent is None:
        return []
    else:
        return parents_of(node.parent) + [
            (type(node.parent.node).__name__, node.parent_attr),
        ]


class AstGenerator:
    def __init__(
        self,
        seed: int | float | str | bytes | bytearray | None = None,
        node_limit: int = 10000000,
        depth_limit: int = 8,
    ) -> None:
        self.rand = random.Random(seed)
        self.nodes = 0
        self.node_limit = node_limit
        self.depth_limit = depth_limit

    def cnd(self) -> bool:
        return self.rand.choice([True, False])

    def fix_result(self, result: ast.AST | None) -> ast.AST:
        """Hook to post-process a generated AST. Accept None during generation.

        Subclasses should override. Default raises NotImplementedError to
        preserve previous behavior.
        """
        raise NotImplementedError

    # --- helper stubs so static type checkers know these exist ---
    def probability_try(
        self, parents: Sequence[tuple[str, str]], child_name: str
    ) -> float:
        """Return probability for child_name given parents or raise Invalid.

        Real implementations live elsewhere; default raises Invalid to signal
        an undefined decision point.
        """
        raise Invalid

    def same_length(self) -> dict:
        return {}

    def min_attr_length(self, type_name: str, attr_name: str) -> int:
        return 0

    def none_allowed(self, parents: Sequence[tuple[str, str]]) -> bool:
        return True

    def fix(
        self, node: ast.AST | None, parents: Sequence[tuple[str, str]]
    ) -> ast.AST | None:
        return node

    def use(self) -> bool:
        return True

    def probability(self, parents: Sequence[tuple[str, str]], child_name: str) -> float:
        try:
            return self.probability_try(parents, child_name)
        except Invalid:
            return 0

    def is_valid_ast(
        self, tree: ast.AST, print: Callable[..., None] = lambda *args: None
    ) -> bool:
        def is_valid(node: ast.AST, parents):
            type_name = node.__class__.__name__
            if (
                isinstance(node, (ast.AST))
                and parents
                and self.probability(
                    parents,
                    type_name,
                )
                == 0
            ):
                print("invalid node with:")
                print("parents:", parents)
                print("node:", node)

                try:
                    self.probability_try(
                        parents,
                        node.__class__.__name__,
                    )
                except Invalid:
                    frame = traceback.extract_tb(sys.exc_info()[2])[1]
                    print("file:", f"{frame.filename}:{frame.lineno}")

                return False

            same_length = self.same_length()

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

                    if isinstance(value, list) and len(value) < self.min_attr_length(
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
                                and self.none_allowed(
                                    parents + [(type_name, attr_name)]
                                )
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
                                fix_tree(
                                    v, parents + [(node.__class__.__name__, field)]
                                )
                                if isinstance(v, ast.AST)
                                else v
                            )
                            for v in value
                        ],
                    )

            return self.fix(node, parents)

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

        tree_copy = self.fix_result(tree_copy)
        if not check_if_changed(tree, tree_copy, "fix_result"):
            return False

        return True

    def generate(self, ast_type_name: str, depth: int = 0) -> ast.AST:
        result = None

        def place(node):
            nonlocal result
            result = node
            return NodeRef(None, "", None, node)

        self.generate_impl(place, None, ast_type_name, [], depth)

        self.fix(result, [])
        result = self.fix_result(result)
        return result

    def context_before(
        self, context: Context | None, node: NodeRef, attr: str, index: int | None
    ) -> Context | None:
        pass

    def context_after(self, context: Context | None, node: NodeRef) -> Context | None:
        pass

    def generate_NodeType(
        self,
        place: Callable[[GeneratedValue], NodeRef],
        parent_node: NodeRef | None,
        info: NodeType,
        ast_type_name: str,
        parents: Sequence[tuple[str, str]],
        depth: int,
        stop: bool,
    ) -> None:
        ranges = {}
        new_result = info.ast_type()
        new_node = place(new_result)
        assert parents_of(new_node) == parents, (parents_of(parent_node), parents)

        def attr_length(child, attr_name):
            if ast_type_name == "Module":
                return 20

            same_length = self.same_length()

            if ast_type_name in same_length:
                attrs = same_length[ast_type_name]
                if attr_name in attrs[1:]:
                    return attr_length(child, attrs[0])

            if child == "arguments" and attr_name == "defaults":
                # defaults of function arguments map to args and posonlyargs (but not all have default args)
                min = 0
                max = attr_length(child, "posonlyargs") + attr_length(child, "args")
                ranges[attr_name] = self.rand.randint(min, max)

            elif attr_name not in ranges:
                min = self.min_attr_length(child, attr_name)

                max = min if stop else min + 1 if depth > 10 else min + 5
                ranges[attr_name] = self.rand.randint(min, max)

            return ranges[attr_name]

        for attr_name, (node_type, quantity) in info.fields.items():
            if "*" in quantity:
                setattr(new_result, attr_name, [])

                def child_place(node):

                    lst = getattr(new_result, attr_name)
                    lst.append(node)
                    return NodeRef(new_node, attr_name, len(lst) - 1, node)

            else:

                def child_place(node):
                    setattr(new_result, attr_name, node)
                    return NodeRef(new_node, attr_name, None, node)

            new_parents = [*parents, (ast_type_name, attr_name)]

            def gen():
                if "?" in quantity and self.none_allowed(new_parents) and self.cnd():
                    child_place(None)
                else:
                    self.generate_impl(
                        child_place, new_node, node_type, new_parents, depth
                    )

            if "*" in quantity:
                for _ in range(attr_length(ast_type_name, attr_name)):
                    gen()
            else:
                gen()

            value = getattr(new_result, attr_name)
            if isinstance(value, list):
                setattr(
                    new_result, attr_name, [self.fix(v, new_parents) for v in value]
                )
            else:
                setattr(new_result, attr_name, self.fix(value, new_parents))

    def generate_UnionNodeType(
        self,
        place: Callable[[GeneratedValue], NodeRef],
        parent_node: NodeRef | None,
        info: UnionNodeType,
        ast_type_name: str,
        parents: Sequence[tuple[str, str]],
        depth: int,
        stop: bool,
    ) -> None:
        # assert parents==parents_of(parent_node),(parents,parents_of(parent_node))

        options_list = [
            (option, self.probability(parents, option)) for option in info.options
        ]

        # check if an invalid can actually be valid (test_valid_source.py)
        invalid_option = [
            option for (option, prop) in options_list if prop == 0 and not self.use()
        ]

        assert len(invalid_option) in (0, 1), invalid_option

        if len(invalid_option) == 1:
            self.generate_impl(place, parent_node, invalid_option[0], parents, depth)
            return

        options = dict(options_list)
        if stop:
            for final in ("Name", "MatchValue", "Pass"):
                if options.get(final, 0) != 0:
                    options = {final: 1}
                    break

        if sum(options.values()) == 0:
            # TODO: better handling of `type?`
            return None

        self.generate_impl(
            place,
            parent_node,
            self.rand.choices(*zip(*options.items()))[0],
            parents,
            depth,
        )

    def generate_BuiltinNodeType(
        self,
        place: Callable[[GeneratedValue], NodeRef],
        parent_node: NodeRef | None,
        info: BuiltinNodeType,
        ast_type_name: str,
        parents: Sequence[tuple[str, str]],
        depth: int,
        stop: bool,
    ) -> None:
        result: str | int | float | bytes | bool | None
        if info.kind == "identifier":
            result = f"name_{self.rand.randint(0,5)}"
        elif info.kind == "int":
            result = self.rand.randint(0, 5)
        elif info.kind == "string":
            result = self.rand.choice(["some text", ""])
        elif info.kind == "constant":
            result = self.rand.choice(
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

        place(result)

    def generate_impl(
        self,
        place: Callable[[GeneratedValue], NodeRef],
        parent_node: NodeRef | None,
        ast_type_name: str,
        parents: Sequence[tuple[str, str]] = (),
        depth: int = 0,
    ) -> None:
        depth += 1
        self.nodes += 1

        if depth > 100:
            exit()

        stop = depth > self.depth_limit or self.nodes > self.node_limit

        info = get_info(ast_type_name)

        getattr(self, f"generate_{type(info).__name__}")(
            place, parent_node, info, ast_type_name, parents, depth, stop
        )
