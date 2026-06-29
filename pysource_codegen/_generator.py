from __future__ import annotations

import ast
import random
import sys
from dataclasses import dataclass
from dataclasses import fields as _dc_fields
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


_dataclass_slots: dict = {"slots": True} if sys.version_info >= (3, 10) else {}


@dataclass(**_dataclass_slots)
class Context:
    """Mutable scope-tracking context threaded through the generator.

    Copied once per context_before call; the copy is then mutated in place.
    Requires Python 3.10+ (dataclass slots=True).
    """

    # True in positions where an Await expression can be used.
    can_await: bool = False
    in_async_context: bool = False
    in_loop: bool = False
    # True inside FunctionDef/AsyncFunctionDef/Lambda body (reset at ClassDef body)
    in_function: bool = False
    # True inside any function/lambda/class body
    in_function_or_class: bool = False
    # True inside Try.finalbody / TryStar.finalbody (reset at function boundary)
    in_finally: bool = False
    # True inside TryStar.handlers (reset at function boundary)
    in_trystar_handler: bool = False
    # True inside a MatchValue node
    in_match_value: bool = False
    # True inside MatchValue.value AND also inside Attribute.value
    in_match_value_attr_chain: bool = False
    # True inside MatchValue AND inside a UnaryOp
    in_match_value_unaryop: bool = False
    # True inside MatchClass.cls
    in_match_class_cls: bool = False
    # Capture names planned for the current match_case pattern
    match_case_names: frozenset[str] = frozenset()
    # Capture names that still need to be bound in the current pattern subtree
    match_required_names: frozenset[str] = frozenset()
    # Capture names already bound while generating the current pattern subtree
    match_used_names: frozenset[str] = frozenset()
    # True while generating a direct MatchOr alternative pattern
    in_match_or_pattern: bool = False
    # Node id and frozen required names for the current MatchOr alternatives
    match_or_node_id: int | None = None
    match_or_required_names: frozenset[str] = frozenset()
    # True while generating a match_case pattern, even when no names are planned
    in_match_case_pattern: bool = False
    # True inside any comprehension node (GeneratorExp/ListComp/SetComp/DictComp)
    in_comprehension: bool = False
    # True inside ClassDef.body but NOT inside a nested function/lambda
    in_class_not_function: bool = False
    # True inside any annotation-like position: ClassDef.bases/keywords,
    # FunctionDef/AsyncFunctionDef.returns, arg.annotation, TypeAlias.value,
    # TypeVar.bound, and (3.13+) type-param default_value fields.
    # NOTE: superset of in_annotation_return_scope and in_type_scope.
    # Rules should prefer the narrower flags (in_type_scope, in_annotation_return_scope,
    # in_ann_assign_annotation) rather than this broad flag.
    in_annotation_scope: bool = False
    # True inside AnnAssign.annotation
    in_ann_assign_annotation: bool = False
    # True inside TypeAlias.value when also inside ClassDef.body
    in_type_alias_in_class: bool = False
    # True inside AnnAssign.target
    in_ann_assign_target: bool = False
    # True inside Delete.targets but not behind Subscript.value/slice or Attribute.value
    in_delete_target: bool = False
    # True inside TypeAlias.value or TypeVar.bound (type parameter scope)
    in_type_scope: bool = False
    # True inside a comprehension whose outer non-function scope is a type scope.
    # Walrus (:=) escapes comprehension scopes, so it would still target the type scope
    # (which has no enclosing function frame) → SyntaxError.
    # Cleared at function/lambda/class body boundaries (where walrus assigns locally).
    in_comprehension_in_type_scope: bool = False
    # True inside a SetComp/ListComp/DictComp that is nested inside AnnAssign.annotation
    # (without an intervening function/class/GeneratorExp boundary).
    # On py314+, the annotation becomes a separate non-async code object (PEP 649),
    # so await inside a set/list/dict comprehension inside the annotation is a SyntaxError
    # ("asynchronous comprehension outside of an asynchronous function").
    # GeneratorExp is excluded: (await x for x in y) creates an async generator
    # expression, which is valid to define in any context (it is lazy/not immediately
    # executed in the surrounding code object).
    # NOT cleared at SetComp/ListComp/DictComp boundaries (nested comprehensions stay).
    # Cleared at function/lambda/class/GeneratorExp boundaries.
    in_comprehension_in_ann_assign_annotation: bool = False
    # True inside a SetComp/ListComp/DictComp that is nested inside an
    # annotation-return-scope position (arg.annotation, FunctionDef.returns,
    # AsyncFunctionDef.returns) without an intervening function/class/GeneratorExp
    # boundary.  Same reasoning as in_comprehension_in_ann_assign_annotation: on
    # py314+, these positions become non-async lazy code objects (PEP 649), so await
    # inside a set/list/dict comprehension there is a SyntaxError
    # ("asynchronous comprehension outside of an asynchronous function").
    # NOT cleared at SetComp/ListComp/DictComp boundaries (nested comprehensions stay).
    # Cleared at function/lambda/class/GeneratorExp boundaries.
    in_comprehension_in_annotation_return_scope: bool = False
    # True inside arg.annotation, FunctionDef.returns, or AsyncFunctionDef.returns.
    # These three positions become lazily-evaluated code objects under PEP 649 (3.14+),
    # which makes := a SyntaxError there even though it is valid in ClassDef.bases etc.
    # Use this flag when a restriction applies *only* to these PEP-649 positions, not
    # to the broader set covered by in_annotation_scope.
    in_annotation_return_scope: bool = False
    # Nesting depth of FormattedValue.format_spec in the ancestor chain
    fstring_format_depth: int = 0
    # Nesting depth of FormattedValue.value in the ancestor chain
    fstring_value_depth: int = 0
    # True when the nearest non-Tuple/List/Starred ancestor is a store-target position
    # (Assign.targets, For.target, AnnAssign.target, AugAssign.target, NamedExpr.target,
    #  TypeAlias.name, withitem.optional_vars, comprehension.target, AsyncFor.target)
    in_store_target: bool = False
    # True inside the Subscript.slice that belongs to an AnnAssign.target subscript
    # (including through nested Tuple/List elts).  Starred is a SyntaxError in this
    # position on py311+ even though it is valid in regular assignment Subscript.slices.
    in_ann_assign_subscript_slice: bool = False
    # True when inside AnnAssign.target and the AnnAssign already has a non-None
    # value.  Meaningful only when in_ann_assign_target is True.  Requires that
    # attr_order generates AnnAssign.value before AnnAssign.target.
    ann_assign_has_value: bool = (
        False  # True inside FunctionDef.returns, AsyncFunctionDef.returns, arg.annotation of a
    )
    # type-parameterized function, OR ClassDef.bases/ClassDef.keywords of a
    # type-parameterized class, when the function/class is nested inside a ClassDef.
    # On Python 3.12 (not 3.13+), comprehensions and lambdas in these annotation
    # positions raise SyntaxError ("Cannot use comprehension/lambda in annotation scope
    # within class scope").  Requires attr_order to generate type_params before
    # args/returns/bases/keywords for FunctionDef/AsyncFunctionDef/ClassDef.
    # Cleared at function/lambda/class body and comprehension elt/key/value boundaries.
    in_typed_func_annotation_in_class: bool = (
        False  # True when inside AsyncFunctionDef.body (transitively through comprehensions),
    )

    def copy(self) -> Context:
        new = Context.__new__(Context)
        for name in _CONTEXT_FIELD_NAMES:
            object.__setattr__(new, name, getattr(self, name))
        return new


_CONTEXT_FIELD_NAMES: tuple[str, ...] = tuple(f.name for f in _dc_fields(Context))


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
                self.parent_signature(),
            ]

    def parent_signature(self) -> tuple[str, str]:
        return (type(self.parent.node).__name__, self.parent_attr)

    def has_parents(self, parents: list[tuple[str, str]]):
        if not parents:
            return True
        if self.parent is None:
            return False
        if parents[-1] == self.parent_signature():
            return self.parent.has_parents(parents[:-1])
        return False

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
        n = self
        i = 0
        while n.parent is not None:
            i += 1
            n = n.parent
        return i

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

    def none_allowed(self, child: NodeRef) -> bool:
        return True

    def fix(self, node: ast.AST, parent: NodeRef, context: Context) -> ast.AST:
        return node

    def use(self, condition: bool = True) -> bool:
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
        self,
        context: Context,
        child_context: Context,
        node: NodeRef,
        attr: str,
        index: int | None,
        value: GeneratedValue,
    ) -> None:
        return None

    def attr_order(self, ast_type_name: str, field_names: list[str]) -> list[str]:
        """Return the order in which the fields of *ast_type_name* are generated.

        Default: definition order (same as *field_names*).  Override to control
        which fields are generated first so that earlier fields are already set
        on ``node.node`` when ``context_before`` is called for later fields.
        """
        return field_names

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

    def attr_length_provider(
        self, parent_node: NodeRef, context: Context | None = None
    ):
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
        context: Context | None = None,
    ) -> bool:
        return "?" in quantity and self.none_allowed(child_parent_node) and self.cnd()

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
        new_result = info.ast_type.__new__(info.ast_type)
        new_node = place(new_result)

        attr_length = self.attr_length_provider(new_node, context)

        for attr_name in self.attr_order(ast_type_name, list(info.fields.keys())):
            node_type, quantity = info.fields[attr_name]

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

            def store_fixed_child(index: int | None, child_context: Context) -> None:
                value = getattr(new_result, attr_name, None)
                if isinstance(value, list):
                    fixed = self.fix(
                        value[index],  # type: ignore[index]
                        new_node.new_child(value[index], attr_name, index),  # type: ignore[index]
                        child_context,
                    )
                    value[index] = fixed  # type: ignore[index]
                else:
                    fixed = self.fix(
                        value, new_node.new_child(value, attr_name), child_context
                    )
                    setattr(new_result, attr_name, fixed)
                self.context_after(
                    context, child_context, new_node, attr_name, index, fixed
                )

            def gen():
                if "*" in quantity:
                    current_idx = len(getattr(new_result, attr_name))
                    child_parent_node = new_node.unknown_attr(attr_name, current_idx)
                else:
                    current_idx = None
                    child_parent_node = new_node.unknown_attr(attr_name)
                child_context = self.context_before(
                    context, new_node, attr_name, current_idx
                )
                if self._should_place_none(
                    child_parent_node, quantity, new_node, child_context
                ):
                    child_place(None)
                else:
                    self.generate_impl(
                        child_place, child_parent_node, node_type, depth, child_context
                    )
                store_fixed_child(current_idx, child_context)

            if "*" in quantity:
                for _ in range(attr_length(attr_name, stop)):
                    gen()
            else:
                gen()

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
            for final in (
                "Name",
                "MatchValue",
                "MatchSingleton",
                "Constant",
                "MatchAs",
                "Pass",
            ):
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

        # if depth > 100:
        #     exit()

        stop = depth > self.depth_limit or self.nodes > self.node_limit

        info = get_info(ast_type_name)

        getattr(self, f"generate_{type(info).__name__}")(
            place, parent_node, info, ast_type_name, depth, stop, context
        )
