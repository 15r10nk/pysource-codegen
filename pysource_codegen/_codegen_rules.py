from __future__ import annotations

import ast
import itertools
import sys
from typing import Callable
from typing import Iterable
from typing import Sequence

from ._limits import f_string_expr_limit
from ._limits import f_string_format_limit
from ._utils import arguments
from ._utils import only_firstone
from ._utils import unique_by
from ._utils import walk_childs_first
from ._utils import walk_function_nodes
from pysource_codegen._generator import AstGenerator
from pysource_codegen._generator import Context
from pysource_codegen._generator import Invalid
from pysource_codegen._generator import NodeRef

py38plus = (3, 8) <= sys.version_info
py39plus = (3, 9) <= sys.version_info
py310plus = (3, 10) <= sys.version_info
py311plus = (3, 11) <= sys.version_info
py312plus = (3, 12) <= sys.version_info

comprehensions = ("GeneratorExp", "ListComp", "SetComp", "DictComp")

InterpolationOrFormattedValue = (ast.FormattedValue,)
if sys.version_info >= (3, 14):
    InterpolationOrFormattedValue += (ast.Interpolation,)  # type: ignore


def all_args(args: ast.arguments) -> tuple[list[ast.arg], ...]:
    if py38plus:
        return (args.posonlyargs, args.args, args.kwonlyargs)
    else:
        return (args.args, args.kwonlyargs)


if sys.version_info >= (3, 10):

    def match_wildcard(node: ast.AST) -> bool:
        if isinstance(node, ast.MatchAs):
            return (
                node.pattern is None
                or match_wildcard(node.pattern)
                or node.name is None
            )
        if isinstance(node, ast.MatchOr):
            return any(match_wildcard(p) for p in node.patterns)

        # default: not a wildcard
        return False

    # @lambda f:lambda pattern:set(f(pattern))
    def all_names(node: ast.AST):  # type: ignore[misc]
        if isinstance(node, ast.MatchAs) and node.name:  # type: ignore[union-attr]
            yield node.name  # type: ignore[union-attr]
        elif isinstance(node, ast.MatchStar) and node.name:  # type: ignore[union-attr]
            yield node.name  # type: ignore[union-attr]
        elif isinstance(node, ast.MatchMapping) and node.rest:  # type: ignore[union-attr]
            yield node.rest  # type: ignore[union-attr]
        elif isinstance(node, ast.MatchOr):  # type: ignore[attr-defined]
            yield from set.intersection(
                *[set(all_names(pattern)) for pattern in node.patterns]  # type: ignore[union-attr]
            )
        else:
            for child in ast.iter_child_nodes(node):
                yield from all_names(child)

    class RemoveName(ast.NodeVisitor):
        def __init__(self, condition: Callable[[str | None], bool]) -> None:
            self.condition = condition

        def visit_MatchAs(self, node: ast.MatchAs) -> None:  # type: ignore[attr-defined]
            if self.condition(node.name):  # type: ignore[union-attr]
                node.name = None  # type: ignore[union-attr]

        def visit_MatchMapping(self, node: ast.MatchMapping) -> None:  # type: ignore[attr-defined]
            if self.condition(node.rest):  # type: ignore[union-attr]
                node.rest = None  # type: ignore[union-attr]

    class RemoveNameCleanup(ast.NodeTransformer):
        def visit_MatchAs(  # type: ignore[attr-defined]
            self, node: ast.MatchAs
        ) -> ast.AST | list[ast.AST] | None:
            if node.name is None and node.pattern is not None:  # type: ignore[union-attr]
                return self.visit(node.pattern)  # type: ignore[union-attr]
            return self.generic_visit(node)

    class FixPatternNames(ast.NodeTransformer):
        def __init__(
            self, used: set[str] | None = None, allowed: set[str] | None = None
        ) -> None:
            # variables which are already used
            self.used: set[str] = set() if used is None else set(used)
            # variables which are allowed in a MatchOr
            self.allowed: set[str] | None = allowed

        def is_allowed(self, name: str | None) -> bool:
            return (
                name is None
                or name not in self.used
                and (name in self.allowed if self.allowed is not None else True)
            )

        def visit_MatchAs(  # type: ignore[attr-defined]
            self, node: ast.MatchAs
        ) -> ast.AST | list[ast.AST] | None:
            if not self.is_allowed(node.name):  # type: ignore[union-attr]
                return ast.MatchSingleton(value=None)  # type: ignore[attr-defined]
            elif node.name is not None:  # type: ignore[union-attr]
                self.used.add(node.name)  # type: ignore[union-attr]
            return self.generic_visit(node)

        def visit_MatchStar(  # type: ignore[attr-defined]
            self, node: ast.MatchStar
        ) -> ast.AST | list[ast.AST] | None:
            if not self.is_allowed(node.name):  # type: ignore[union-attr]
                return ast.MatchSingleton(value=None)  # type: ignore[attr-defined]
            elif node.name is not None:  # type: ignore[union-attr]
                self.used.add(node.name)  # type: ignore[union-attr]
            return self.generic_visit(node)

        def visit_MatchMapping(  # type: ignore[attr-defined]
            self, node: ast.MatchMapping
        ) -> ast.AST | list[ast.AST] | None:
            if not self.is_allowed(node.rest):  # type: ignore[union-attr]
                return ast.MatchSingleton(value=None)  # type: ignore[attr-defined]
            elif node.rest is not None:  # type: ignore[union-attr]
                self.used.add(node.rest)  # type: ignore[union-attr]
            return self.generic_visit(node)

        def visit_MatchOr(self, node: ast.MatchOr) -> ast.MatchOr:  # type: ignore[attr-defined]
            allowed = set.intersection(
                *[set(all_names(pattern)) for pattern in node.patterns]  # type: ignore[union-attr]
            )
            allowed -= self.used

            node.patterns = [  # type: ignore[union-attr]
                FixPatternNames(set(self.used), allowed).visit(child)  # type: ignore[arg-type]
                for child in node.patterns  # type: ignore[union-attr]
            ]

            self.used |= allowed

            return node


class StdGenerator(AstGenerator):

    def use(self) -> bool:
        """
        this function is mocked in test_valid_source to ignore some decisions
        which are usually made by the algo.
        The goal is to try to generate some valid source code which would otherwise not be generated,
        becaus the algo falsely thinks it is invalid.
        """
        return True

    def probability_try(
        self, node: NodeRef, child_name: str, context: Context
    ) -> float:
        par = node.parent
        gpar = par.parent  # type: ignore[union-attr]
        p_type = type(par.node).__name__  # type: ignore[union-attr]
        p_attr = node.parent_attr
        p_info = (p_type, p_attr)

        if child_name in ("Store", "Del", "Load"):
            return 1

        child_method = self._child_dispatch.get(child_name)
        if child_method is not None:
            result = child_method(
                self, node, par, gpar, p_type, p_attr, p_info, context
            )
            if result is not None:
                return result

        # f-string structural exclusions
        if p_info == ("JoinedStr", "values") and child_name not in (
            "Constant",
            "FormattedValue",
        ):
            raise Invalid

        if 0:
            if (
                not py312plus
                and p_info == ("FormattedValue", "value")
                and child_name != "Constant"
            ):
                # TODO: WHY?
                raise Invalid

        if p_info == ("FormattedValue", "format_spec") and child_name != "JoinedStr":
            raise Invalid

        if context.in_delete_target and child_name not in (
            "Name",
            "Attribute",
            "Subscript",
            "List",
            "Tuple",
        ):
            raise Invalid

        assign_target = ("Subscript", "Attribute", "Name", "Starred", "List", "Tuple")

        if context.in_store_target and child_name not in assign_target:
            raise Invalid

        if p_info == ("AnnAssign", "target"):
            if child_name not in ("Name", "Attribute", "Subscript"):
                raise Invalid

        if p_info == ("NamedExpr", "target") and child_name != "Name":
            raise Invalid

        if p_info == ("MatchMapping", "keys") and child_name != "Constant":
            # TODO: find all allowed key types
            raise Invalid

        if context.in_match_value and child_name not in (
            "Attribute",
            "Name",
            "Constant",
            "UnaryOp",
            "USub",
        ):
            raise Invalid

        if context.in_match_value_attr_chain and child_name not in (
            "Attribute",
            "Name",
        ):
            raise Invalid

        if context.in_match_class_cls:
            if child_name not in ("Name", "Attribute"):
                raise Invalid

        if not py39plus:
            parents = node.all_parents()
            if any(p[1] == "decorator_list" for p in parents):
                # restricted decorators
                # see https://peps.python.org/pep-0614/

                deco_parents = list(
                    itertools.takewhile(
                        lambda a: a[1] != "decorator_list", reversed(parents)
                    )
                )[::-1]

                def valid_deco_parents(parents: Sequence[tuple[str, str]]) -> bool:
                    # Call?,Attribute*
                    parents = list(parents)
                    if parents and parents[0] == ("Call", "func"):
                        parents.pop()
                    return all(p == ("Attribute", "value") for p in parents)

                if valid_deco_parents(deco_parents) and child_name != "Name":
                    raise Invalid

        # type alias
        if py312plus:
            if p_info == ("TypeAlias", "name") and child_name != "Name":
                raise Invalid

        if sys.version_info >= (3, 14):
            if p_info == ("TemplateStr", "values") and child_name not in (
                "Interpolation",
                "Constant",
            ):
                raise Invalid

            if p_info == ("Interpolation", "format_spec") and child_name != "JoinedStr":
                raise Invalid

        return 1

    def probability_try_Attribute(
        self,
        node: NodeRef,
        par: NodeRef,
        gpar: NodeRef | None,
        p_type: str,
        p_attr: str,
        p_info: tuple[str, str],
        context: Context,
    ) -> float | None:
        if context.in_match_value_unaryop:
            raise Invalid
        return None

    def probability_try_AsyncFor(
        self,
        node: NodeRef,
        par: NodeRef,
        gpar: NodeRef | None,
        p_type: str,
        p_attr: str,
        p_info: tuple[str, str],
        context: Context,
    ) -> float | None:
        if not context.in_async_code:
            raise Invalid
        return None

    def probability_try_AsyncWith(
        self,
        node: NodeRef,
        par: NodeRef,
        gpar: NodeRef | None,
        p_type: str,
        p_attr: str,
        p_info: tuple[str, str],
        context: Context,
    ) -> float | None:
        if not context.in_async_code:
            raise Invalid
        return None

    def probability_try_Await(
        self,
        node: NodeRef,
        par: NodeRef,
        gpar: NodeRef | None,
        p_type: str,
        p_attr: str,
        p_info: tuple[str, str],
        context: Context,
    ) -> float | None:
        if not context.in_async_code:
            # await is also valid in a GeneratorExp's inner scope:
            # - any comprehension's ifs clause
            # - non-first comprehension's iter (generators[1:].iter)
            in_genexp_inner = (
                p_type == "comprehension"
                and gpar is not None
                and type(gpar.node).__name__ == "GeneratorExp"
                and (
                    p_attr == "ifs"
                    or (
                        p_attr == "iter"
                        and par.parent_attr_index is not None
                        and par.parent_attr_index > 0
                    )
                )
            )
            if not in_genexp_inner:
                raise Invalid
        if py312plus and (
            context.in_ann_assign_annotation or context.in_annotation_scope
        ):
            raise Invalid
        return None

    def probability_try_Break(
        self,
        node: NodeRef,
        par: NodeRef,
        gpar: NodeRef | None,
        p_type: str,
        p_attr: str,
        p_info: tuple[str, str],
        context: Context,
    ) -> float | None:
        if not context.in_loop:
            raise Invalid
        if context.in_trystar_handler:
            # SyntaxError: 'break', 'continue' and 'return' cannot appear in an except* block
            raise Invalid
        return None

    def probability_try_Continue(
        self,
        node: NodeRef,
        par: NodeRef,
        gpar: NodeRef | None,
        p_type: str,
        p_attr: str,
        p_info: tuple[str, str],
        context: Context,
    ) -> float | None:
        if not py38plus and context.in_finally:
            raise Invalid
        if not context.in_loop:
            raise Invalid
        if context.in_trystar_handler:
            # SyntaxError: 'break', 'continue' and 'return' cannot appear in an except* block
            raise Invalid
        return None

    def probability_try_DictComp(
        self,
        node: NodeRef,
        par: NodeRef,
        gpar: NodeRef | None,
        p_type: str,
        p_attr: str,
        p_info: tuple[str, str],
        context: Context,
    ) -> float | None:
        if (
            py312plus
            and (context.in_annotation_scope or context.in_ann_assign_annotation)
            and context.in_async_code
        ):
            raise Invalid
        return None

    def probability_try_Expr(
        self,
        node: NodeRef,
        par: NodeRef,
        gpar: NodeRef | None,
        p_type: str,
        p_attr: str,
        p_info: tuple[str, str],
        context: Context,
    ) -> float | None:
        return 30

    def probability_try_ExtSlice(
        self,
        node: NodeRef,
        par: NodeRef,
        gpar: NodeRef | None,
        p_type: str,
        p_attr: str,
        p_info: tuple[str, str],
        context: Context,
    ) -> float | None:
        if p_info == ("ExtSlice", "dims"):
            # SystemError('extended slice invalid in nested slice')
            raise Invalid
        return None

    def probability_try_FormattedValue(
        self,
        node: NodeRef,
        par: NodeRef,
        gpar: NodeRef | None,
        p_type: str,
        p_attr: str,
        p_info: tuple[str, str],
        context: Context,
    ) -> float | None:
        if p_type != "JoinedStr":
            # TODO: doc says this should be valid, maybe a bug in the python doc
            # see https://github.com/python/cpython/issues/111257
            raise Invalid
        return None

    def probability_try_GeneratorExp(
        self,
        node: NodeRef,
        par: NodeRef,
        gpar: NodeRef | None,
        p_type: str,
        p_attr: str,
        p_info: tuple[str, str],
        context: Context,
    ) -> float | None:
        if (
            py312plus
            and (context.in_annotation_scope or context.in_ann_assign_annotation)
            and context.in_async_code
        ):
            raise Invalid
        return None

    def probability_try_Interpolation(
        self,
        node: NodeRef,
        par: NodeRef,
        gpar: NodeRef | None,
        p_type: str,
        p_attr: str,
        p_info: tuple[str, str],
        context: Context,
    ) -> float | None:
        if sys.version_info >= (3, 14) and p_type != "TemplateStr":
            raise Invalid
        return None

    def probability_try_JoinedStr(
        self,
        node: NodeRef,
        par: NodeRef,
        gpar: NodeRef | None,
        p_type: str,
        p_attr: str,
        p_info: tuple[str, str],
        context: Context,
    ) -> float | None:
        if (
            context.fstring_format_depth > f_string_format_limit
            or context.fstring_value_depth > f_string_expr_limit
        ):
            raise Invalid
        return None

    def probability_try_Lambda(
        self,
        node: NodeRef,
        par: NodeRef,
        gpar: NodeRef | None,
        p_type: str,
        p_attr: str,
        p_info: tuple[str, str],
        context: Context,
    ) -> float | None:
        if py312plus and context.in_type_alias_in_class and sys.version_info < (3, 13):
            # SyntaxError('Cannot use lambda in annotation scope within class scope')
            raise Invalid
        return None

    def probability_try_List(
        self,
        node: NodeRef,
        par: NodeRef,
        gpar: NodeRef | None,
        p_type: str,
        p_attr: str,
        p_info: tuple[str, str],
        context: Context,
    ) -> float | None:
        if p_info in (("AugAssign", "target"), ("AnnAssign", "target")):
            raise Invalid
        return None

    def probability_try_ListComp(
        self,
        node: NodeRef,
        par: NodeRef,
        gpar: NodeRef | None,
        p_type: str,
        p_attr: str,
        p_info: tuple[str, str],
        context: Context,
    ) -> float | None:
        if (
            py312plus
            and (context.in_annotation_scope or context.in_ann_assign_annotation)
            and context.in_async_code
        ):
            raise Invalid
        return None

    def probability_try_MatchStar(
        self,
        node: NodeRef,
        par: NodeRef,
        gpar: NodeRef | None,
        p_type: str,
        p_attr: str,
        p_info: tuple[str, str],
        context: Context,
    ) -> float | None:
        if p_type != "MatchSequence":
            raise Invalid
        return None

    def probability_try_Name(
        self,
        node: NodeRef,
        par: NodeRef,
        gpar: NodeRef | None,
        p_type: str,
        p_attr: str,
        p_info: tuple[str, str],
        context: Context,
    ) -> float | None:
        if context.in_match_value_unaryop:
            raise Invalid
        if p_info == ("MatchValue", "value"):
            raise Invalid
        return None

    def probability_try_NamedExpr(
        self,
        node: NodeRef,
        par: NodeRef,
        gpar: NodeRef | None,
        p_type: str,
        p_attr: str,
        p_info: tuple[str, str],
        context: Context,
    ) -> float | None:
        if p_info == ("comprehension", "iter"):
            raise Invalid
        if context.in_comprehension and context.in_class_not_function:
            # SyntaxError: assignment expression within a comprehension cannot be used in a class body
            raise Invalid
        if py312plus and context.in_type_scope:
            # todo this should only be invalid in type scopes (when the class/def has type parameters)
            # and only for async comprehensions
            raise Invalid
        if sys.version_info >= (3, 14) and context.in_annotation_return_scope:
            raise Invalid
        return None

    def probability_try_NonLocal(
        self,
        node: NodeRef,
        par: NodeRef,
        gpar: NodeRef | None,
        p_type: str,
        p_attr: str,
        p_info: tuple[str, str],
        context: Context,
    ) -> float | None:
        if p_info == ("Module", "body"):
            raise Invalid
        return None

    def probability_try_Nonlocal(
        self,
        node: NodeRef,
        par: NodeRef,
        gpar: NodeRef | None,
        p_type: str,
        p_attr: str,
        p_info: tuple[str, str],
        context: Context,
    ) -> float | None:
        # function statements
        if not context.in_function_or_class:
            raise Invalid
        return None

    def probability_try_Return(
        self,
        node: NodeRef,
        par: NodeRef,
        gpar: NodeRef | None,
        p_type: str,
        p_attr: str,
        p_info: tuple[str, str],
        context: Context,
    ) -> float | None:
        if not context.in_function:
            raise Invalid
        if context.in_trystar_handler:
            # SyntaxError: 'break', 'continue' and 'return' cannot appear in an except* block
            raise Invalid
        return None

    def probability_try_SetComp(
        self,
        node: NodeRef,
        par: NodeRef,
        gpar: NodeRef | None,
        p_type: str,
        p_attr: str,
        p_info: tuple[str, str],
        context: Context,
    ) -> float | None:
        if (
            py312plus
            and (context.in_annotation_scope or context.in_ann_assign_annotation)
            and context.in_async_code
        ):
            raise Invalid
        return None

    def probability_try_Slice(
        self,
        node: NodeRef,
        par: NodeRef,
        gpar: NodeRef | None,
        p_type: str,
        p_attr: str,
        p_info: tuple[str, str],
        context: Context,
    ) -> float | None:
        if not (
            p_info == ("Subscript", "slice")
            or (
                p_info == ("Tuple", "elts")
                and gpar is not None
                and (type(gpar.node).__name__, par.parent_attr) == ("Subscript", "slice")  # type: ignore[union-attr]
            )
        ):
            raise Invalid
        return None

    def probability_try_Starred(
        self,
        node: NodeRef,
        par: NodeRef,
        gpar: NodeRef | None,
        p_type: str,
        p_attr: str,
        p_info: tuple[str, str],
        context: Context,
    ) -> float | None:
        # py311+: *args can have a TypeVarTuple annotation: def f(*x: *Ts)
        if (
            py311plus
            and p_info == ("arg", "annotation")
            and par.parent_attr == "vararg"
        ):
            return None
        if p_info not in (
            ("Tuple", "elts"),
            ("Call", "args"),
            ("List", "elts"),
            ("Set", "elts"),
            ("ClassDef", "bases"),
        ):
            raise Invalid
        if context.in_ann_assign_target:
            # TODO this might be a cpython bug
            raise Invalid
        return None

    def probability_try_Tuple(
        self,
        node: NodeRef,
        par: NodeRef,
        gpar: NodeRef | None,
        p_type: str,
        p_attr: str,
        p_info: tuple[str, str],
        context: Context,
    ) -> float | None:
        if p_info in (("AugAssign", "target"), ("AnnAssign", "target")):
            raise Invalid
        return None

    def probability_try_UnaryOp(
        self,
        node: NodeRef,
        par: NodeRef,
        gpar: NodeRef | None,
        p_type: str,
        p_attr: str,
        p_info: tuple[str, str],
        context: Context,
    ) -> float | None:
        if context.in_match_value_unaryop:
            raise Invalid
        return None

    def probability_try_Yield(
        self,
        node: NodeRef,
        par: NodeRef,
        gpar: NodeRef | None,
        p_type: str,
        p_attr: str,
        p_info: tuple[str, str],
        context: Context,
    ) -> float | None:
        if not context.in_function:
            raise Invalid
        if context.in_comprehension:
            # SyntaxError: 'yield' inside list comprehension
            raise Invalid
        if py312plus and context.in_annotation_scope:
            # todo this should only be invalid in type scopes (when the class/def has type parameters)
            # and only for async comprehensions
            raise Invalid
        return None

    def probability_try_YieldFrom(
        self,
        node: NodeRef,
        par: NodeRef,
        gpar: NodeRef | None,
        p_type: str,
        p_attr: str,
        p_info: tuple[str, str],
        context: Context,
    ) -> float | None:
        if not context.in_function:
            raise Invalid
        if context.in_async_code:
            raise Invalid
        if context.in_comprehension:
            # SyntaxError: 'yield' inside list comprehension
            raise Invalid
        if py312plus and context.in_annotation_scope:
            # todo this should only be invalid in type scopes (when the class/def has type parameters)
            # and only for async comprehensions
            raise Invalid
        return None

    def context_before(
        self, context: Context, node: NodeRef, attr: str, index: int | None
    ) -> Context:
        node_type = type(node.node).__name__
        is_function_def = node_type in ("FunctionDef", "AsyncFunctionDef", "Lambda")
        ctx = context.copy()

        # --- in_async_code ---
        if not ctx.in_async_code and (node_type, attr) in (
            ("AsyncFunctionDef", "body"),
            ("GeneratorExp", "elt"),
        ):
            ctx.in_async_code = True
        elif (
            ctx.in_async_code
            and attr == "body"
            and node_type
            in (
                "FunctionDef",
                "Lambda",
                "ClassDef",
            )
        ):
            ctx.in_async_code = False

        # --- in_async_context (stricter: only AsyncFunctionDef.body activates) ---
        if node_type == "AsyncFunctionDef" and attr == "body":
            ctx.in_async_context = True
        elif node_type in ("FunctionDef", "Lambda", "ClassDef", "TypeAlias"):
            ctx.in_async_context = False
        elif (node_type, attr) in (
            ("AsyncFunctionDef", "returns"),
            ("arg", "annotation"),
            ("TypeVar", "bound"),
        ):
            ctx.in_async_context = False
        elif not py311plus and node_type in comprehensions:
            ctx.in_async_context = False

        # --- in_loop ---
        if attr == "body" and node_type in ("For", "While", "AsyncFor"):
            ctx.in_loop = True
        elif attr == "body" and node_type in (
            "FunctionDef",
            "Lambda",
            "AsyncFunctionDef",
            "ClassDef",
        ):
            ctx.in_loop = False

        # --- in_excepthandler ---
        if node_type == "ExceptHandler":
            ctx.in_excepthandler = True
        elif is_function_def:
            ctx.in_excepthandler = False

        # --- in_function: inside FunctionDef/AsyncFunctionDef/Lambda body, reset at ClassDef.body ---
        if attr == "body" and is_function_def:
            ctx.in_function = True
        elif attr == "body" and node_type == "ClassDef":
            ctx.in_function = False

        # --- in_function_or_class: inside any function/lambda/class body ---
        if attr == "body" and node_type in (
            "FunctionDef",
            "AsyncFunctionDef",
            "Lambda",
            "ClassDef",
        ):
            ctx.in_function_or_class = True

        # --- in_finally: inside Try.finalbody / TryStar.finalbody, reset at function boundary ---
        if attr == "finalbody" and node_type in ("Try", "TryStar"):
            ctx.in_finally = True
        elif attr == "body" and is_function_def:
            ctx.in_finally = False

        # --- in_trystar_handler: inside TryStar.handlers, reset at function boundary ---
        if attr == "handlers" and node_type == "TryStar":
            ctx.in_trystar_handler = True
        elif attr == "body" and is_function_def:
            ctx.in_trystar_handler = False

        # --- in_match_value: inside a MatchValue node ---
        if node_type == "MatchValue":
            ctx.in_match_value = True

        # --- in_match_value_attr_chain: inside MatchValue.value and also inside Attribute.value ---
        if ctx.in_match_value and node_type == "Attribute" and attr == "value":
            ctx.in_match_value_attr_chain = True
        elif not ctx.in_match_value:
            ctx.in_match_value_attr_chain = False

        # --- in_match_value_unaryop: inside MatchValue AND inside a UnaryOp ---
        if ctx.in_match_value and node_type == "UnaryOp":
            ctx.in_match_value_unaryop = True
        elif not ctx.in_match_value:
            ctx.in_match_value_unaryop = False

        # --- in_match_class_cls: inside MatchClass.cls (propagates through Attribute.value chain) ---
        ctx.in_match_class_cls = (node_type == "MatchClass" and attr == "cls") or (
            ctx.in_match_class_cls and node_type == "Attribute" and attr == "value"
        )

        # --- in_comprehension: inside any comprehension node ---
        if node_type in comprehensions:
            ctx.in_comprehension = True
        elif is_function_def or node_type == "ClassDef":
            ctx.in_comprehension = False

        # --- in_class_not_function: inside ClassDef.body but not nested function/lambda ---
        if attr == "body" and node_type == "ClassDef":
            ctx.in_class_not_function = True
        elif is_function_def:
            ctx.in_class_not_function = False

        # --- in_annotation_scope: annotation/type-alias positions where yield/await/walrus forbidden ---
        if (node_type, attr) in (
            ("ClassDef", "bases"),
            ("ClassDef", "keywords"),
            ("FunctionDef", "returns"),
            ("AsyncFunctionDef", "returns"),
            ("arg", "annotation"),
            ("TypeAlias", "value"),
            ("TypeVar", "bound"),
            # py3.13+: type param defaults also forbid walrus/yield/await
            ("TypeVar", "default_value"),
            ("TypeVarTuple", "default_value"),
            ("ParamSpec", "default_value"),
        ):
            ctx.in_annotation_scope = True
        elif attr == "body" and node_type in (
            "FunctionDef",
            "AsyncFunctionDef",
            "Lambda",
            "ClassDef",
        ):
            ctx.in_annotation_scope = False

        # --- in_ann_assign_annotation: inside AnnAssign.annotation ---
        if node_type == "AnnAssign" and attr == "annotation":
            ctx.in_ann_assign_annotation = True
        elif attr == "body" and node_type in (
            "FunctionDef",
            "AsyncFunctionDef",
            "Lambda",
        ):
            ctx.in_ann_assign_annotation = False

        # --- in_type_alias_in_class: inside TypeAlias.value when also inside ClassDef.body ---
        if node_type == "TypeAlias" and attr == "value" and ctx.in_class_not_function:
            ctx.in_type_alias_in_class = True
        elif is_function_def:
            ctx.in_type_alias_in_class = False

        # --- in_ann_assign_target: inside AnnAssign.target ---
        ctx.in_ann_assign_target = node_type == "AnnAssign" and attr == "target"

        # --- in_delete_target: inside Delete.targets, cleared once inside sub-expression ---
        if node_type == "Delete" and attr == "targets":
            ctx.in_delete_target = True
        elif ctx.in_delete_target and (node_type, attr) in (
            ("Subscript", "value"),
            ("Subscript", "slice"),
            ("Attribute", "value"),
        ):
            ctx.in_delete_target = False

        # --- in_type_scope: inside TypeAlias.value or TypeVar.bound ---
        if (node_type, attr) in (("TypeAlias", "value"), ("TypeVar", "bound")):
            ctx.in_type_scope = True
        elif attr == "body" and node_type in (
            "FunctionDef",
            "AsyncFunctionDef",
            "Lambda",
            "ClassDef",
        ):
            ctx.in_type_scope = False

        # --- in_annotation_return_scope: inside arg.annotation / FunctionDef.returns / AsyncFunctionDef.returns ---
        if (node_type, attr) in (
            ("arg", "annotation"),
            ("FunctionDef", "returns"),
            ("AsyncFunctionDef", "returns"),
        ):
            ctx.in_annotation_return_scope = True
        elif attr == "body" and node_type in (
            "FunctionDef",
            "AsyncFunctionDef",
            "Lambda",
            "ClassDef",
        ):
            ctx.in_annotation_return_scope = False

        # --- fstring_format_depth: count FormattedValue.format_spec ancestors ---
        if (node_type, attr) == ("FormattedValue", "format_spec"):
            ctx.fstring_format_depth += 1

        # --- fstring_value_depth: count FormattedValue.value ancestors ---
        if (node_type, attr) == ("FormattedValue", "value"):
            ctx.fstring_value_depth += 1

        # --- in_store_target: transparent through Tuple/List/Starred ---
        if (node_type, attr) in (
            ("For", "target"),
            ("AsyncFor", "target"),
            ("AnnAssign", "target"),
            ("AugAssign", "target"),
            ("Assign", "targets"),
            ("withitem", "optional_vars"),
            ("comprehension", "target"),
            ("NamedExpr", "target"),
            ("TypeAlias", "name"),
        ):
            ctx.in_store_target = True
        elif not (ctx.in_store_target and node_type in ("Tuple", "List", "Starred")):
            ctx.in_store_target = False

        return ctx

    def fix(self, node: ast.AST, parent_node: NodeRef, context: Context) -> ast.AST:
        p_attr = parent_node.parent_attr
        p_type = (
            type(parent_node.parent.node).__name__
            if parent_node.parent is not None and parent_node.parent.node is not None
            else ""
        )
        p_info = (p_type, p_attr)

        if isinstance(node, ast.ImportFrom):
            if self.use() and not py310plus and node.level is None:
                node.level = 0

            if (
                self.use()
                and node.module is None
                and (node.level is None or node.level == 0)
            ):
                node.level = 1

        if isinstance(node, ast.ExceptHandler):
            if self.use() and node.type is None:
                node.name = None

        if (
            sys.version_info < (3, 11)
            and isinstance(node, ast.Tuple)
            and p_info == ("Subscript", "slice")
        ):
            # a[(a:b,*c)] <- not valid
            # TODO check this
            found = False
            new_elts: list[ast.expr] = []
            # allow only the first Slice or Starred
            for e in node.elts:
                if isinstance(e, (ast.Starred, ast.Slice)):
                    if not found:
                        new_elts.append(e)
                        found = True
                else:
                    new_elts.append(e)
            node.elts = new_elts

        if (
            self.use()
            and isinstance(node, ast.AnnAssign)
            and not isinstance(node.target, ast.Name)
        ):
            node.simple = 0

        if isinstance(node, ast.Constant):
            # TODO: what is Constant.kind
            # Constant.kind can be u for unicode strings
            allowed_kind: list[str | None] = [None]
            if isinstance(node.value, str):
                allowed_kind.append("u")
            elif node.kind not in allowed_kind:
                node.kind = allowed_kind[hash(node.kind) % len(allowed_kind)]

            if (
                self.use()
                and (
                    p_info == ("JoinedStr", "values")
                    or p_info == ("TemplateStr", "values")
                )
                and not isinstance(node.value, str)
            ):
                # TODO: better format string generation
                node.value = str(node.value)

        if isinstance(node, InterpolationOrFormattedValue):
            valid_conversion = (-1, 115, 114, 97)
            if self.use() and not py310plus and node.conversion is None:
                node.conversion = 5
            if self.use() and node.conversion not in valid_conversion:
                node.conversion = valid_conversion[node.conversion % 4]

        if hasattr(node, "ctx"):
            if self.use() and context.in_delete_target:
                node.ctx = ast.Del()
            elif self.use() and context.in_store_target:
                node.ctx = ast.Store()
            else:
                node.ctx = ast.Load()

        if (
            self.use()
            and isinstance(node, (ast.List, ast.Tuple))
            and isinstance(node.ctx, ast.Store)
        ):
            only_firstone(node.elts, lambda e: isinstance(e, ast.Starred))

        if self.use() and isinstance(
            node, (ast.AsyncFunctionDef, ast.FunctionDef, ast.Lambda)
        ):
            # unique argument names
            seen = set()
            for args in all_args(node.args):
                for i, arg in reversed(list(enumerate(args))):
                    if arg.arg in seen:
                        del args[i]
                        if node.args.defaults:
                            del node.args.defaults[0]
                    seen.add(arg.arg)

            for arg_name in ("kwarg", "vararg"):
                arg = getattr(node.args, arg_name)
                if arg:
                    if arg.arg in seen:
                        setattr(node.args, arg_name, None)
                    seen.add(arg.arg)
            arguments = node.args
            # kwonlyargs and kw_defaults has to have the same size
            min_kw_size = min(len(arguments.kwonlyargs), len(arguments.kw_defaults))
            arguments.kwonlyargs = arguments.kwonlyargs[:min_kw_size]
            arguments.kw_defaults = arguments.kw_defaults[:min_kw_size]

        if self.use() and isinstance(node, ast.AsyncFunctionDef):
            if any(
                isinstance(n, (ast.Yield, ast.YieldFrom))
                for n in walk_function_nodes(node.body)
            ):
                for n in walk_function_nodes(node.body):
                    if isinstance(n, ast.Return):
                        n.value = None

        if self.use() and isinstance(node, (ast.ClassDef, ast.Call)):
            # unique argument names
            seen = set()
            for i, kw in reversed(list(enumerate(node.keywords))):
                if kw.arg:
                    if kw.arg in seen:
                        del node.keywords[i]
                    seen.add(kw.arg)

        if self.use() and isinstance(node, (ast.Try)):
            node.handlers[:-1] = [
                handler for handler in node.handlers[:-1] if handler.type is not None
            ]
            if self.use() and not node.handlers:
                node.orelse = []

        if self.use() and isinstance(
            node, (ast.GeneratorExp, ast.ListComp, ast.DictComp, ast.SetComp)
        ):
            # SyntaxError: assignment expression cannot rebind comprehension iteration variable 'name_3'
            names = {
                n.id
                for c in node.generators
                for n in ast.walk(c.target)
                if isinstance(n, ast.Name)
            } | {
                n.id
                for c in node.generators
                for n in ast.walk(c.iter)
                if isinstance(n, ast.Name)
            }
            use = self.use

            class Transformer(ast.NodeTransformer):
                def visit_NamedExpr(
                    self, node: ast.NamedExpr
                ) -> ast.AST | list[ast.AST] | None:
                    if use() and node.target.id in names:
                        return self.visit(node.value)
                    return self.generic_visit(node)

            node = Transformer().visit(node)

        # pattern matching
        if sys.version_info >= (3, 10):

            if isinstance(node, ast.Match):
                found = False
                new_last = None
                for i, case_ in reversed(list(enumerate(node.cases))):
                    p = case_.pattern
                    if match_wildcard(p) and case_.guard is None:
                        if not found:
                            new_last = node.cases[i]
                            found = True
                        del node.cases[i]
                if new_last:
                    node.cases.append(new_last)

            if (
                isinstance(node, ast.MatchValue)
                and isinstance(node.value, ast.UnaryOp)
                and isinstance(node.value.operand, ast.Constant)
                and type(node.value.operand.value) not in (int, float)
            ):
                node.value = node.value.operand

            if (
                isinstance(node, ast.MatchValue)
                and isinstance(node.value, ast.Constant)
                and any(node.value.value is v for v in (None, True, False))
                and isinstance(node.value.value, (type(None), bool))
            ):
                return ast.MatchSingleton(value=node.value.value)

            if isinstance(node, ast.MatchSingleton) and not any(
                node.value is v for v in (None, True, False)
            ):
                return ast.MatchValue(value=ast.Constant(value=node.value))

            if isinstance(node, ast.match_case):
                node.pattern = FixPatternNames().visit(node.pattern)

            if isinstance(node, ast.MatchMapping):

                def can_literal_eval(node):
                    try:
                        hash(ast.literal_eval(node))
                    except ValueError:
                        return False
                    return True

                node.keys = [k for k in node.keys if can_literal_eval(k)]

                node.keys = unique_by(node.keys, ast.literal_eval)
                del node.patterns[len(node.keys) :]

                seen = set()
                for pattern in node.patterns:
                    RemoveName(lambda name: name in seen).visit(pattern)
                    seen |= {*all_names(pattern)}

            if isinstance(node, ast.MatchOr):
                var_names = set.intersection(
                    *[set(all_names(pattern)) for pattern in node.patterns]
                )

                RemoveName(lambda name: name not in var_names).visit(node)

                for i, pattern in enumerate(node.patterns):
                    if match_wildcard(pattern):
                        node.patterns = node.patterns[: i + 1]
                        break

                if len(node.patterns) == 1:
                    return node.patterns[0]

            if isinstance(node, ast.Match):
                for i, case in enumerate(node.cases):
                    # default match `case _:`
                    if (
                        isinstance(case.pattern, ast.MatchAs)
                        and case.pattern.name is None
                        or isinstance(case.pattern, ast.MatchOr)
                        and isinstance(case.pattern.patterns[-1], ast.MatchAs)
                        and case.pattern.patterns[-1].name is None
                        and case.guard is None
                    ):
                        node.cases = node.cases[: i + 1]
                        break

            if isinstance(node, ast.MatchSequence):
                only_firstone(node.patterns, lambda e: isinstance(e, ast.MatchStar))

                seen = set()
                for pattern in node.patterns:
                    RemoveName(lambda name: name in seen).visit(pattern)
                    seen |= {*all_names(pattern)}

            if isinstance(node, ast.MatchClass):
                node.kwd_attrs = unique_by(node.kwd_attrs, lambda e: e)
                del node.kwd_patterns[len(node.kwd_attrs) :]

                seen = set()
                for pattern in [*node.patterns, *node.kwd_patterns]:
                    RemoveName(lambda name: name in seen).visit(pattern)
                    seen |= {*all_names(pattern)}

            if isinstance(node, ast.Match):
                node = RemoveNameCleanup().visit(node)

        if isinstance(node, (ast.ListComp, ast.SetComp, ast.DictComp)):
            if self.use() and not context.in_async_context:
                for comp in node.generators:
                    comp.is_async = 0

        if isinstance(node, ast.Raise):
            if self.use() and not node.exc:
                node.cause = None

        if self.use() and isinstance(node, ast.Lambda):
            # no annotation for lambda arguments
            for args in all_args(node.args):
                for arg in args:
                    arg.annotation = None

            if self.use() and node.args.vararg:
                node.args.vararg.annotation = None

            if self.use() and node.args.kwarg:
                node.args.kwarg.annotation = None

        if (
            self.use()
            and isinstance(node, InterpolationOrFormattedValue)
            and isinstance(node.format_spec, ast.JoinedStr)
        ):
            for const in node.format_spec.values:
                if isinstance(const, ast.Constant):
                    assert isinstance(const.value, str)
                    const.value = const.value.replace("{", "").replace("}", "")

        if sys.version_info >= (3, 12):

            use = self.use
            # type scopes
            if self.use() and hasattr(node, "type_params"):
                node.type_params = unique_by(node.type_params, lambda p: p.name)

            def cleanup_annotation(annotation):
                class Transformer(ast.NodeTransformer):
                    def visit_NamedExpr(self, node: ast.NamedExpr):
                        if not use():
                            return self.generic_visit(node)
                        return self.visit(node.value)

                    def visit_Yield(
                        self, node: ast.Yield
                    ) -> ast.AST | list[ast.AST] | None:
                        if not use():
                            return self.generic_visit(node)
                        if node.value is None:
                            return ast.Constant(value=None)
                        return self.visit(node.value)

                    def visit_YieldFrom(
                        self, node: ast.YieldFrom
                    ) -> ast.AST | list[ast.AST] | None:
                        if not use():
                            return self.generic_visit(node)
                        return self.visit(node.value)

                    # def visit_Lambda(self, node: ast.Lambda) -> ast.AST | list[ast.AST] | None:
                    #     if not use():
                    #         return self.generic_visit(node)
                    #     return self.visit(node.body)

                return Transformer().visit(annotation)

            if (
                isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                and node.type_params
            ):
                for func_arg in [
                    *node.args.posonlyargs,
                    *node.args.args,
                    *node.args.kwonlyargs,
                    node.args.vararg,
                    node.args.kwarg,
                ]:
                    if (
                        self.use()
                        and func_arg is not None
                        and func_arg.annotation is not None
                    ):
                        func_arg.annotation = cleanup_annotation(func_arg.annotation)

                if self.use() and node.returns is not None:
                    node.returns = cleanup_annotation(node.returns)

            if isinstance(node, ast.ClassDef) and node.type_params:
                node.bases = [cleanup_annotation(b) for b in node.bases]
                for kw in node.keywords:
                    if self.use():
                        kw.value = cleanup_annotation(kw.value)

                for n in ast.walk(node):
                    if self.use() and isinstance(n, ast.TypeAlias):
                        n.value = cleanup_annotation(n.value)

            if isinstance(node, ast.ClassDef):
                for n in ast.walk(node):
                    if (
                        self.use()
                        and isinstance(n, ast.TypeVar)
                        and n.bound is not None
                    ):
                        n.bound = cleanup_annotation(n.bound)

            if self.use() and isinstance(node, ast.AnnAssign):
                node.annotation = cleanup_annotation(node.annotation)

        if sys.version_info >= (3, 13):
            if hasattr(node, "type_params"):
                # non-default type parameter 'name_1' follows default type parameter
                # All default params must come at the end: clear defaults from any
                # param that appears (in forward order) before a non-default param.
                no_default_seen = False
                for child in reversed(node.type_params):
                    if child.default_value is None:
                        no_default_seen = True
                    elif no_default_seen and self.use():
                        child.default_value = None

        if sys.version_info >= (3, 14):
            if (
                self.use()
                and isinstance(node, ast.Interpolation)
                and isinstance(node.value, ast.Constant)
            ):
                node.value.value = str(node.value.value)

        return node

    def fix_result(self, node: ast.AST) -> ast.AST:
        if sys.version_info >= (3, 14):
            for n in walk_childs_first(node):
                if self.use() and isinstance(n, ast.Interpolation):
                    f_str = ast.JoinedStr(
                        [
                            ast.FormattedValue(
                                value=n.value, conversion=-1, format_spec=None
                            )
                        ]
                    )
                    f_str_repr = ast.unparse(f_str)
                    if f_str_repr.startswith(("f'''", 'f"""')):
                        n.str = ast.unparse(f_str)[5:-4]  # strip f"""{...}"""
                    else:
                        n.str = ast.unparse(f_str)[3:-2]  # strip f"{...}"

        return self.fix_nonlocal(node)

    def fix_nonlocal(self, node: ast.AST) -> ast.AST:
        class NonLocalFixer(ast.NodeTransformer):
            """
            removes invalid Nonlocals from the class/function
            """

            def __init__(
                self,
                locals: Iterable[str],
                nonlocals: Iterable[str],
                globals: Iterable[str],
                type_params: Iterable[str],
                parent_globals: Iterable[str],
                is_module_scope: bool = False,
            ) -> None:
                self.locals: set[str] = set(locals)
                self.used_names: set[str] = set(locals)
                self.type_params: set[str] = set(type_params)

                # nonlocals from the parent scope
                self.nonlocals: set[str] = set(nonlocals)
                self.used_nonlocals: set[str] = set()

                # globals from the global scope
                self.globals: set[str] = set(globals)
                self.used_globals: set[str] = set()
                self.parent_globals = parent_globals
                self.is_module_scope = is_module_scope

            def name_assigned(self, name: str) -> None:
                self.locals.add(name)
                self.used_names.add(name)

            def visit_Name(self, node: ast.Name) -> ast.AST | list[ast.AST] | None:
                if isinstance(node.ctx, (ast.Store, ast.Del)):
                    self.name_assigned(node.id)
                else:
                    self.used_names.add(node.id)
                return node

            if sys.version_info >= (3, 10):

                def visit_MatchAs(
                    self, node: ast.MatchAs
                ) -> ast.AST | list[ast.AST] | None:
                    if node.pattern:
                        self.visit(node.pattern)
                    if node.name is not None:
                        self.name_assigned(node.name)
                    return node

            def search_walrus(self, node: ast.AST) -> None:
                for n in ast.walk(node):
                    if isinstance(n, ast.NamedExpr):
                        self.visit(n.target)

            def visit_GeneratorExp(
                self, node: ast.GeneratorExp
            ) -> ast.AST | list[ast.AST] | None:
                self.visit(node.generators[0].iter)
                self.search_walrus(node)
                return node

            def visit_ListComp(
                self, node: ast.ListComp
            ) -> ast.AST | list[ast.AST] | None:
                self.visit(node.generators[0].iter)
                self.search_walrus(node)
                return node

            def visit_DictComp(
                self, node: ast.DictComp
            ) -> ast.AST | list[ast.AST] | None:
                self.visit(node.generators[0].iter)
                self.search_walrus(node)
                return node

            def visit_SetComp(
                self, node: ast.SetComp
            ) -> ast.AST | list[ast.AST] | None:
                self.visit(node.generators[0].iter)
                self.search_walrus(node)
                return node

            def visit_Nonlocal(
                self, node: ast.Nonlocal
            ) -> ast.AST | list[ast.AST] | None:
                # TODO: research __class__ seems to be defined in the class scope
                # but it is also not
                # class A:
                #     print(locals()) # no __class__
                #     def f():
                #         nonlocal __class__ # is A
                node.names = [
                    name
                    for name in node.names
                    if name not in self.locals
                    and name in self.nonlocals
                    and name not in self.used_names
                    and name not in self.type_params
                    and name not in self.parent_globals
                    and name not in self.used_globals
                    or name in ("__class__",)
                ]
                self.used_nonlocals |= set(node.names)

                if not node.names:
                    return ast.Pass()

                return node

            def visit_Global(self, node: ast.Global) -> ast.AST | list[ast.AST] | None:
                node.names = [
                    name
                    for name in node.names
                    if name not in self.locals
                    and name not in self.used_names
                    and name not in self.used_nonlocals
                ]
                self.used_globals |= set(node.names)

                if not node.names:
                    return ast.Pass()

                return node

            def visit_AnnAssign(
                self, node: ast.AnnAssign
            ) -> ast.AST | list[ast.AST] | None:
                if (
                    not self.is_module_scope
                    and isinstance(node.target, ast.Name)
                    and (
                        node.target.id in self.used_globals
                        or node.target.id in self.used_nonlocals
                    )
                ):
                    if node.value:
                        return self.generic_visit(
                            ast.Assign(
                                targets=[node.target],
                                value=node.value,
                                type_comment=None,
                            )
                        )
                    else:
                        return ast.Pass()
                return self.generic_visit(node)

            def visit_FunctionDef(
                self, node: ast.FunctionDef
            ) -> ast.AST | list[ast.AST] | None:
                if node.name is not None:
                    self.name_assigned(node.name)

                all_nodes = [
                    *node.args.defaults,
                    *node.args.kw_defaults,
                    *node.decorator_list,
                    node.returns,
                ]

                all_nodes += [arg.annotation for arg in arguments(node)]

                for default in all_nodes:
                    if default is not None:
                        self.visit(default)

                return node

            def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> ast.AST:
                self.name_assigned(node.name)

                all_nodes = [
                    *node.args.defaults,
                    *node.args.kw_defaults,
                    *node.decorator_list,
                    node.returns,
                ]

                all_nodes += [arg.annotation for arg in arguments(node)]

                for default in all_nodes:
                    if default is not None:
                        self.visit(default)
                return node

            def visit_ClassDef(
                self, node: ast.ClassDef
            ) -> ast.AST | list[ast.AST] | None:
                for expr in [
                    *[k.value for k in node.keywords],
                    *node.bases,
                    *node.decorator_list,
                ]:
                    if expr is not None:
                        self.visit(expr)

                self.name_assigned(node.name)

                return node

            # pattern matching
            if sys.version_info >= (3, 10):

                def visit_MatchMapping(
                    self, node: ast.MatchMapping
                ) -> ast.AST | list[ast.AST] | None:
                    if node.rest is not None:
                        self.name_assigned(node.rest)
                    return self.generic_visit(node)

            if sys.version_info >= (3, 13):

                def visit_MatchStar(self, node: ast.MatchStar):
                    if node.name:
                        self.name_assigned(node.name)
                    return self.generic_visit(node)

            def visit_ExceptHandler(
                self, handler: ast.ExceptHandler
            ) -> ast.AST | list[ast.AST] | None:
                if handler.name:
                    self.name_assigned(handler.name)
                return self.generic_visit(handler)

            def visit_Lambda(self, node: ast.Lambda) -> ast.AST | list[ast.AST] | None:
                for default in [*node.args.defaults, *node.args.kw_defaults]:
                    if default is not None:
                        self.visit(default)
                return node

            if sys.version_info < (3, 13):

                try_attrs = ("body", "orelse", "handlers", "finalbody")

                def visit_Try(self, node: ast.Try) -> ast.AST | list[ast.AST] | None:
                    # work around for https://github.com/python/cpython/issues/111123
                    args = {
                        k: [self.visit(x) for x in getattr(node, k)]
                        for k in self.try_attrs
                    }

                    assert set(self.try_attrs) == set(ast.Try._fields)

                    return ast.Try(**args)  # type: ignore

                if sys.version_info >= (3, 11):

                    def visit_TryStar(
                        self, node: ast.TryStar
                    ) -> ast.AST | list[ast.AST] | None:
                        # work around for https://github.com/python/cpython/issues/111123
                        args = {
                            k: [self.visit(x) for x in getattr(node, k)]
                            for k in self.try_attrs
                        }

                        assert set(self.try_attrs) == set(ast.TryStar._fields)

                        return ast.TryStar(**args)  # type: ignore

        class FunctionTransformer(ast.NodeTransformer):
            """
            - transformes a class/function
            """

            def __init__(
                self,
                nonlocals: Iterable[str],
                globals: Iterable[str],
                type_params: Iterable[str],
                parent_globals: Iterable[str],
            ) -> None:
                self.nonlocals = set(nonlocals)
                self.globals = set(globals)
                self.type_params = type_params
                self.parent_globals = parent_globals

            def visit_FunctionDef(
                self, node: ast.FunctionDef
            ) -> ast.AST | list[ast.AST] | None:
                return self.handle_function(node)

            def visit_AsyncFunctionDef(
                self, node: ast.AsyncFunctionDef
            ) -> ast.AST | list[ast.AST] | None:
                return self.handle_function(node)

            def visit_Lambda(self, node: ast.Lambda) -> ast.AST | list[ast.AST] | None:
                # there are no globals/nonlocals/functiondefs in lambdas
                return node

            def visit_ClassDef(
                self, node: ast.ClassDef
            ) -> ast.AST | list[ast.AST] | None:
                type_params = set(self.type_params)
                if sys.version_info >= (3, 12):
                    type_params |= {typ.name for typ in node.type_params}  # type: ignore

                fixer = NonLocalFixer(
                    [], self.nonlocals, self.globals, type_params, self.parent_globals
                )
                node.body = [fixer.visit(stmt) for stmt in node.body]

                ft = FunctionTransformer(
                    self.nonlocals, self.globals, type_params, self.parent_globals
                )
                node.body = [ft.visit(stmt) for stmt in node.body]

                return node

            def handle_function(
                self, node: ast.FunctionDef | ast.AsyncFunctionDef
            ) -> ast.AST | list[ast.AST] | None:
                names = {arg.arg for arg in arguments(node)}

                type_params = set(self.type_params)
                if sys.version_info >= (3, 12):
                    type_params |= {typ.name for typ in node.type_params}  # type: ignore

                fixer = NonLocalFixer(
                    names,
                    self.nonlocals,
                    self.globals,
                    type_params,
                    self.parent_globals,
                )
                node.body = [fixer.visit(stmt) for stmt in node.body]

                ft = FunctionTransformer(
                    fixer.locals | self.nonlocals,
                    self.globals,
                    type_params,
                    fixer.used_globals,
                )
                node.body = [ft.visit(stmt) for stmt in node.body]

                return node

        fixer = NonLocalFixer([], [], [], [], [], is_module_scope=True)
        node = fixer.visit(node)

        node = FunctionTransformer([], [], [], []).visit(node)
        return node

    def min_attr_length(self, node_type: str, attr_name: str) -> int:
        attr = f"{node_type}.{attr_name}"
        if node_type == "Module" and attr_name == "body":
            return 0
        if attr_name == "body":
            return 1
        if node_type == "MatchOr" and attr_name == "patterns":
            return 2
        if node_type == "BoolOp" and attr_name == "values":
            return 2
        if node_type == "BinOp" and attr_name == "values":
            return 1
        if node_type == "Import" and attr_name == "names":
            return 1
        if node_type == "ImportFrom" and attr_name == "names":
            return 1
        if node_type in ("With", "AsyncWith") and attr_name == "items":
            return 1
        if node_type in ("Try", "TryStar") and attr_name == "handlers":
            return 1
        if node_type == "Delete" and attr_name == "targets":
            return 1
        if node_type == "Match" and attr_name == "cases":
            return 1
        if node_type == "ExtSlice" and attr_name == "dims":
            return 1
        if sys.version_info < (3, 9, 3) and node_type == "Set" and attr_name == "elts":
            return 1
        if node_type == "Compare" and attr_name in ("ops", "comparators"):
            return 1
        if attr_name == "generators":
            return 1

        if attr == "Assign.targets":
            return 1

        return 0

    def none_allowed(self, child: NodeRef) -> bool:
        # ExceptHandler.type must not be None when ExceptHandler is inside TryStar.handlers
        if (
            child.parent_attr == "type"
            and type(child.parent.node).__name__ == "ExceptHandler"  # type: ignore[union-attr]
            and child.parent.parent is not None  # type: ignore[union-attr]
            and child.parent.parent_attr == "handlers"  # type: ignore[union-attr]
            and type(child.parent.parent.node).__name__ == "TryStar"  # type: ignore[union-attr]
        ):
            return False
        return True

    def same_length(self) -> dict[str, list[str]]:
        return {
            "MatchClass": ["kwd_attrs", "kwd_patterns"],
            "MatchMapping": ["patterns", "keys"],
            "arguments": ["kw_defaults", "kwonlyargs"],
            "Compare": ["ops", "comparators"],
            "Dict": ["keys", "values"],
        }


StdGenerator._child_dispatch = {
    name[len("probability_try_") :]: func
    for name, func in vars(StdGenerator).items()
    if name.startswith("probability_try_")
}
