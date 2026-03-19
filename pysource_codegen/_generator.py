from __future__ import annotations

import ast
import random
from dataclasses import dataclass
from dataclasses import replace
from typing import Callable
from typing import Union

from .ast_info import get_info
from .types import BuiltinNodeType
from .types import NodeType
from .types import UnionNodeType

# A generated value can be either an AST node or one of the builtin leaf values
GeneratedValue = Union[ast.AST, str, int, float, bytes, bool, None]


class Invalid(Exception):
    pass


class Context:
    """Mutable scope-tracking context threaded through the generator.

    Uses __slots__ for fast attribute access and a copy() method for
    branching at each tree node (context_before copies once, then mutates).
    """

    __slots__ = (
        "in_async_code",
        "in_async_context",
        "in_loop",
        "in_excepthandler",
        # True inside FunctionDef/AsyncFunctionDef/Lambda body (reset at ClassDef body)
        "in_function",
        # True inside any function/lambda/class body
        "in_function_or_class",
        # True inside Try.finalbody / TryStar.finalbody (reset at function boundary)
        "in_finally",
        # True inside TryStar.handlers (reset at function boundary)
        "in_trystar_handler",
        # True inside a MatchValue node
        "in_match_value",
        # True inside MatchValue.value AND also inside Attribute.value
        "in_match_value_attr_chain",
        # True inside MatchValue AND inside a UnaryOp
        "in_match_value_unaryop",
        # True inside MatchClass.cls
        "in_match_class_cls",
        # True inside any comprehension node (GeneratorExp/ListComp/SetComp/DictComp)
        "in_comprehension",
        # True inside ClassDef.body but NOT inside a nested function/lambda
        "in_class_not_function",
        # True inside annotation/type-alias scope (returns, annotations, TypeAlias.value, etc.)
        "in_annotation_scope",
        # True inside AnnAssign.annotation
        "in_ann_assign_annotation",
        # True inside TypeAlias.value when also inside ClassDef.body
        "in_type_alias_in_class",
        # True inside AnnAssign.target
        "in_ann_assign_target",
        # True inside Delete.targets but not behind Subscript.value/slice or Attribute.value
        "in_delete_target",
        # True inside TypeAlias.value or TypeVar.bound (type parameter scope)
        "in_type_scope",
        # True inside arg.annotation / FunctionDef.returns / AsyncFunctionDef.returns
        "in_annotation_return_scope",
    )

    def __init__(self) -> None:
        self.in_async_code = False
        self.in_async_context = False
        self.in_loop = False
        self.in_excepthandler = False
        self.in_function = False
        self.in_function_or_class = False
        self.in_finally = False
        self.in_trystar_handler = False
        self.in_match_value = False
        self.in_match_value_attr_chain = False
        self.in_match_value_unaryop = False
        self.in_match_class_cls = False
        self.in_comprehension = False
        self.in_class_not_function = False
        self.in_annotation_scope = False
        self.in_ann_assign_annotation = False
        self.in_type_alias_in_class = False
        self.in_ann_assign_target = False
        self.in_delete_target = False
        self.in_type_scope = False
        self.in_annotation_return_scope = False

    def copy(self) -> Context:
        new = Context.__new__(Context)
        new.in_async_code = self.in_async_code
        new.in_async_context = self.in_async_context
        new.in_loop = self.in_loop
        new.in_excepthandler = self.in_excepthandler
        new.in_function = self.in_function
        new.in_function_or_class = self.in_function_or_class
        new.in_finally = self.in_finally
        new.in_trystar_handler = self.in_trystar_handler
        new.in_match_value = self.in_match_value
        new.in_match_value_attr_chain = self.in_match_value_attr_chain
        new.in_match_value_unaryop = self.in_match_value_unaryop
        new.in_match_class_cls = self.in_match_class_cls
        new.in_comprehension = self.in_comprehension
        new.in_class_not_function = self.in_class_not_function
        new.in_annotation_scope = self.in_annotation_scope
        new.in_ann_assign_annotation = self.in_ann_assign_annotation
        new.in_type_alias_in_class = self.in_type_alias_in_class
        new.in_ann_assign_target = self.in_ann_assign_target
        new.in_delete_target = self.in_delete_target
        new.in_type_scope = self.in_type_scope
        new.in_annotation_return_scope = self.in_annotation_return_scope
        return new


@dataclass
class NodeRef:
    parent: NodeRef | None = None
    parent_attr: str = ""
    parent_attr_index: int | None = None
    node: ast.AST | None = None

    def __getattr__(self, name: str) -> NodeRef | list[NodeRef] | None:
        value = getattr(self.node, name)
        if isinstance(value, list):
            return [NodeRef(self, name, i, n) for i, n in enumerate(value)]
        if value is None:
            return None
        return NodeRef(self, name, None, value)

    def all_parents(self: NodeRef) -> list[tuple[str, str]]:
        if self.parent is None:
            return []
        else:
            return self.parent.all_parents() + [
                (type(self.parent.node).__name__, self.parent_attr),
            ]

    def is_node(self, node):
        assert self.node is None, self
        return replace(self, node=node)

    def unknown_attr(self, attr, index=None):
        return NodeRef(self, attr, index, None)

    def new_child(self, value, attr_name, index=None) -> NodeRef:
        return NodeRef(self, attr_name, index, value)

    def relocate(self, tree) -> NodeRef:
        if self.parent is None:
            return NodeRef(node=tree)

        parent = self.parent.relocate(tree)
        child_node = getattr(parent.node, self.parent_attr)
        if self.parent_attr_index is not None:
            child_node = child_node[self.parent_attr_index]

        return parent.new_child(child_node, self.parent_attr, self.parent_attr_index)

    def depth(self):
        if self.parent is None:
            return 0
        else:
            return self.parent.depth() + 1

    def __repr__(self):
        return self._path() + f": {type(self.node).__name__}"

    def _path(self):
        result = ""
        if self.parent is None:
            result = "root"
        else:
            result = repr(self.parent)
        if self.parent_attr:
            result += f".{self.parent_attr}"
        if self.parent_attr_index:
            result += f"[{self.parent_attr_index}]"
        return result


def parents_of(node: NodeRef | None) -> list[tuple[str, str]]:
    if node:
        return node.all_parents()
    return []


class AstGenerator:
    def __init__(
        self,
        seed: int | float | str | bytes | bytearray | None = None,
        node_limit: int = 10000000,
        depth_limit: int = 8,
    ) -> None:
        self._rand = random.Random(seed)
        self.nodes = 0
        self.node_limit = node_limit
        self.depth_limit = depth_limit

    @property
    def rand(self):
        return self._rand

    def cnd(self) -> bool:
        return self.rand.choice([True, False])

    def fix_result(self, result: ast.AST) -> ast.AST:
        """Hook to post-process a generated AST. Accept None during generation.

        Subclasses should override. Default raises NotImplementedError to
        preserve previous behavior.
        """
        raise NotImplementedError

    # --- helper stubs so static type checkers know these exist ---
    def probability_try(
        self, parent: NodeRef, child_name: str, context: Context
    ) -> float:
        """Return probability for child_name given parents or raise Invalid.

        Real implementations live elsewhere; default raises Invalid to signal
        an undefined decision point.
        """
        raise Invalid

    def same_length(self) -> dict[str, list[str]]:
        return {}

    def min_attr_length(self, type_name: str, attr_name: str) -> int:
        return 0

    def none_allowed(self, parent: NodeRef) -> bool:
        return True

    def fix(self, node: ast.AST, parent: NodeRef, context: Context) -> ast.AST:
        return node

    def use(self) -> bool:
        return True

    def probability(self, node: NodeRef, child_name: str, context: Context) -> float:
        try:
            return self.probability_try(node, child_name, context)
        except Invalid:
            return 0

    def context_before(
        self, context: Context, node: NodeRef, attr: str, index: int | None
    ) -> Context:
        return context

    def context_after(
        self, context: Context, node: NodeRef, attr: str, index: int | None
    ) -> None:
        pass

    def generate(self, ast_type_name: str, depth: int = 0) -> ast.AST:
        result = None
        context = Context()

        def place(node):
            nonlocal result
            result = node
            return NodeRef(None, "", None, node)

        parent_node = NodeRef(None, "", None, None)

        self.generate_impl(place, parent_node, ast_type_name, depth, context)

        assert result is not None

        self.fix(result, parent_node, context)
        result = self.fix_result(result)
        return result

    def attr_length_provider(self, parent_node: NodeRef):
        ast_type_name = type(parent_node.node).__name__
        ranges = {}
        depth = parent_node.depth()

        def attr_length(attr_name, stop):
            if ast_type_name == "Module":
                return 20

            same_length = self.same_length()

            if ast_type_name in same_length:
                attrs = same_length[ast_type_name]
                if attr_name in attrs[1:]:
                    return attr_length(attrs[0], stop)

            if ast_type_name == "arguments" and attr_name == "defaults":
                # defaults of function arguments map to args and posonlyargs (but not all have default args)
                min = 0
                max = attr_length("posonlyargs", stop) + attr_length("args", stop)
                ranges[attr_name] = self.rand.randint(min, max)

            elif attr_name not in ranges:
                min = self.min_attr_length(ast_type_name, attr_name)

                max = min if stop else min + 1 if depth > 10 else min + 5
                ranges[attr_name] = self.rand.randint(min, max)
                return ranges[attr_name]

            return ranges[attr_name]

        return attr_length

    def _should_place_none(
        self,
        child_parent_node: NodeRef,
        quantity: str,
        new_node: NodeRef,
    ) -> bool:
        return "?" in quantity and self.none_allowed(new_node) and self.cnd()

    def generate_NodeType(
        self,
        place: Callable[[GeneratedValue], NodeRef],
        parent_node: NodeRef,
        info: NodeType,
        ast_type_name: str,
        depth: int,
        stop: bool,
        context: Context,
    ) -> None:
        new_result = info.ast_type()
        new_node = place(new_result)

        attr_length = self.attr_length_provider(new_node)

        for attr_name, (node_type, quantity) in info.fields.items():
            child_context = self.context_before(context, new_node, attr_name, None)

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

            def gen():
                if "*" in quantity:
                    current_idx = len(getattr(new_result, attr_name))
                    child_parent_node = new_node.unknown_attr(attr_name, current_idx)
                else:
                    child_parent_node = new_node.unknown_attr(attr_name)
                if self._should_place_none(child_parent_node, quantity, new_node):
                    child_place(None)
                else:
                    self.generate_impl(
                        child_place, child_parent_node, node_type, depth, child_context
                    )

            if "*" in quantity:
                for _ in range(attr_length(attr_name, stop)):
                    gen()
            else:
                gen()

            value = getattr(new_result, attr_name)
            if isinstance(value, list):
                setattr(
                    new_result,
                    attr_name,
                    [
                        self.fix(v, new_node.new_child(v, attr_name, i), child_context)
                        for i, v in enumerate(value)
                    ],
                )
            else:
                setattr(
                    new_result,
                    attr_name,
                    self.fix(
                        value, new_node.new_child(value, attr_name), child_context
                    ),
                )

            self.context_after(child_context, new_node, attr_name, None)

    def generate_UnionNodeType(
        self,
        place: Callable[[GeneratedValue], NodeRef],
        parent_node: NodeRef,
        info: UnionNodeType,
        ast_type_name: str,
        depth: int,
        stop: bool,
        context: Context,
    ) -> None:

        options_list = [
            (option, self.probability(parent_node, option, context))
            for option in info.options
        ]

        # check if an invalid can actually be valid (test_valid_source.py)
        invalid_option = [
            option for (option, prop) in options_list if prop == 0 and not self.use()
        ]

        assert len(invalid_option) in (0, 1), invalid_option

        if len(invalid_option) == 1:
            self.generate_impl(place, parent_node, invalid_option[0], depth, context)
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

        non_zero = [opt for opt, p in options.items() if p != 0]
        chosen = (
            non_zero[0]
            if len(non_zero) == 1
            else self.rand.choices(*zip(*options.items()))[0]
        )

        self.generate_impl(
            place,
            parent_node,
            chosen,
            depth,
            context,
        )

    def generate_BuiltinNodeType(
        self,
        place: Callable[[GeneratedValue], NodeRef],
        parent_node: NodeRef | None,
        info: BuiltinNodeType,
        ast_type_name: str,
        depth: int,
        stop: bool,
        context: Context,
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
        parent_node: NodeRef,
        ast_type_name: str,
        depth: int = 0,
        context: Context = Context(),
    ) -> None:
        depth += 1
        self.nodes += 1

        if depth > 100:
            exit()

        stop = depth > self.depth_limit or self.nodes > self.node_limit

        info = get_info(ast_type_name)

        getattr(self, f"generate_{type(info).__name__}")(
            place, parent_node, info, ast_type_name, depth, stop, context
        )
