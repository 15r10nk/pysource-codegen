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
py391plus = (3, 9, 1) <= sys.version_info  # ast.unparse f-string quoting fixed in 3.9.1
py310plus = (3, 10) <= sys.version_info
py311plus = (3, 11) <= sys.version_info
py312plus = (3, 12) <= sys.version_info
py1223plus = (
    3,
    12,
    3,
) <= sys.version_info  # ast.unparse f-string quoting fixed in 3.12.3
py313plus = (3, 13) <= sys.version_info
py314plus = (3, 14) <= sys.version_info
py315plus = (3, 15) <= sys.version_info

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

    def use(self, condition: bool = True) -> bool:
        """
        Guards a post-generation fix-up step inside ``fix()``.

        Accepts an optional ``condition`` argument.  In normal generation this
        returns ``condition`` directly, so ``use(False)`` short-circuits a
        fix-up whose guard is already ``False`` without consuming a probe slot.

        In the test suite (``test_valid_source``) it is mocked so that it
        returns ``False`` exactly **once** per generation run *and only when
        ``condition`` is ``True``*, systematically skipping each reachable
        fix-up in turn.  The resulting AST is then:

        1. Passed to ``compile()`` — if it raises ``SyntaxError`` the skipped
           fix-up is load-bearing and the variant is discarded.
        2. If it compiles, ``is_valid_ast()`` (the ``AstChecker``) is run on it.
           If the checker returns ``False`` on a tree that *does* compile, a bug
           has been found: the checker wrongly rejects valid Python.  The source
           is saved as a new ``tests/valid_source_samples/`` entry.

        In other words, ``use(condition)`` turns every fix-up branch into a
        probe: skipping it once explores the space of "unfixed but still valid"
        ASTs that the normal generator would never produce, hunting for checker
        blind spots.  The ``condition`` argument prevents wasting probe slots on
        branches whose guard is already ``False``.
        """
        return condition

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
                        parents.pop(0)
                    return all(p == ("Attribute", "value") for p in parents)

                # At the top of decorator_list, Call and Attribute are also
                # valid (e.g. @name() or @name.attr).  Inside Call.func /
                # Attribute.value chains only Name and Attribute are allowed.
                allowed_deco = (
                    {"Name", "Attribute", "Call"}
                    if not deco_parents
                    else {"Name", "Attribute"}
                )
                if valid_deco_parents(deco_parents) and child_name not in allowed_deco:
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
            # On <3.14, AnnAssign.annotation inside a function body is
            # evaluated inside the function's own scope, so the Python
            # compiler accepts `await` there even for sync functions.
            # However, this only works when there IS a function frame — at
            # module level or in a class body await is still a SyntaxError.
            # (arg.annotation and returns are evaluated in the *enclosing*
            # scope — NOT covered here; they always forbid await below.)
            in_unevaluated_annotation = (
                not py314plus
                and context.in_function
                and (
                    context.in_ann_assign_annotation
                    or context.in_comprehension_in_ann_assign_annotation
                )
            )
            if not in_genexp_inner and not in_unevaluated_annotation:
                raise Invalid
            # in_genexp_inner positions are inside the generator's own implicit
            # function scope.  Annotation-scope restrictions from the surrounding
            # code (e.g. ClassDef.bases/keywords) do not apply there, just as
            # they do not apply inside GeneratorExp.elt (see context_before).
            return None
        # arg.annotation and FunctionDef/AsyncFunctionDef.returns are always
        # evaluated in the *enclosing* scope of the function being defined, not
        # inside the function body.  If the enclosing scope is NOT async, await
        # is a SyntaxError there (already handled above in the not-in_async_code
        # branch).  If it IS async (in_async_code=True), await is valid on <3.14
        # but becomes a SyntaxError on 3.14+ (PEP 649 lazy annotation code objects).
        if py312plus and context.in_type_scope:
            # SyntaxError in type scopes (TypeAlias.value, TypeVar.bound, type-param
            # default_value): no async function frame exists to await in.
            raise Invalid
        if py314plus and (
            context.in_annotation_return_scope
            or context.in_comprehension_in_annotation_return_scope
            or context.in_ann_assign_annotation
            or context.in_comprehension_in_ann_assign_annotation
        ):
            # PEP 649 (3.14+): arg.annotation, returns, and AnnAssign.annotation become
            # lazy code objects, making await a SyntaxError there.  This also covers
            # await inside a comprehension inside those positions, because the
            # comprehension's implicit async code object would sit inside a non-async
            # annotation code object → "asynchronous comprehension outside of an
            # asynchronous function".
            # ClassDef.bases/keywords are still eagerly evaluated, so await is allowed.
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
        if py312plus and (
            context.in_type_scope or context.in_comprehension_in_type_scope
        ):
            # SyntaxError in type scopes (TypeAlias.value, TypeVar.bound, type-param
            # default_value): the lazy evaluation context has no enclosing function
            # frame to assign the walrus target into.
            # Also forbidden when the walrus is inside a comprehension that is itself
            # nested in a type scope: walrus escapes the comprehension boundary, so it
            # would still target the type scope (which has no function frame).
            raise Invalid
        if py314plus and (
            context.in_annotation_return_scope or context.in_ann_assign_annotation
        ):
            # PEP 649: arg.annotation / returns / AnnAssign.annotation become lazy code
            # objects in 3.14+, making := a SyntaxError there.
            # ClassDef.bases/keywords are still eager, so walrus is allowed there.
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
            or p_info == ("ExtSlice", "dims")
            # On 3.8, ExtSlice.dims may contain Slice: e.g. a[:, :] parses as
            # ExtSlice(dims=[Slice(), Slice()]).
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
        # py3.13+: TypeVarTuple default_value is a Starred expression: def f[*Ts = *int]()
        if py313plus and p_info == ("TypeVarTuple", "default_value"):
            return None
        # py3.15+: starred expressions are allowed as comprehension elements
        # (e.g. {*x for x in y}, [*x for x in y], (*x for x in y)) — but NOT
        # in DictComp.key or DictComp.value.
        if py315plus and p_info in (
            ("SetComp", "elt"),
            ("ListComp", "elt"),
            ("GeneratorExp", "elt"),
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
        if py311plus and context.in_ann_assign_subscript_slice:
            # SyntaxError: can't use starred expression here
            # On py311+ `a[*x,] = y` is valid but `a[*x,]: T` is not.
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
        if py312plus and context.in_type_scope:
            # SyntaxError in type scopes (TypeAlias.value, TypeVar.bound, type-param
            # default_value): no generator function frame exists to yield from.
            raise Invalid
        if py314plus and (
            context.in_annotation_return_scope or context.in_ann_assign_annotation
        ):
            # PEP 649 (3.14+): arg.annotation, returns, and AnnAssign.annotation become
            # lazy code objects, making yield a SyntaxError there.
            # ClassDef.bases/keywords are still eagerly evaluated, so yield is allowed.
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
            # yield from is a SyntaxError in async functions, EXCEPT inside
            # AnnAssign.annotation on <3.14 where annotations are evaluated in
            # the function's own scope.  (arg.annotation / returns are evaluated
            # in the enclosing scope, so yield from is invalid there even when
            # the enclosing scope is async — handled by in_annotation_return_scope
            # which prevents in_function from being True for those positions.)
            if not (not py314plus and context.in_ann_assign_annotation):
                raise Invalid
        if context.in_comprehension:
            # SyntaxError: 'yield' inside list comprehension
            raise Invalid
        if py312plus and context.in_type_scope:
            # SyntaxError in type scopes (TypeAlias.value, TypeVar.bound, type-param
            # default_value): no generator function frame exists for yield from.
            raise Invalid
        if py314plus and (
            context.in_annotation_return_scope or context.in_ann_assign_annotation
        ):
            # PEP 649 (3.14+): arg.annotation, returns, and AnnAssign.annotation become
            # lazy code objects, making yield from a SyntaxError there.
            # ClassDef.bases/keywords are still eagerly evaluated, so yield from is allowed.
            raise Invalid
        return None

    def context_before(
        self, context: Context, node: NodeRef, attr: str, index: int | None
    ) -> Context:
        node_type = type(node.node).__name__
        is_function_def = node_type in ("FunctionDef", "AsyncFunctionDef", "Lambda")
        ctx = context.copy()

        # --- in_async_code ---
        # GeneratorExp.elt is included to allow `await` in the elt of an async
        # genexp (e.g. `(await x async for x in y)`). The comprehension rejection
        # checks (DictComp/GeneratorExp/ListComp/SetComp) do NOT use this flag
        # because: async comprehensions in annotation scopes are already prevented
        # by probability_try_AsyncFor (which requires in_async_code=True, but
        # annotation attrs are generated *before* AsyncFunctionDef.body sets it).
        if not ctx.in_async_code and (node_type, attr) in (
            ("AsyncFunctionDef", "body"),
            ("GeneratorExp", "elt"),
        ):
            ctx.in_async_code = True
        elif ctx.in_async_code and (
            (attr == "body" and node_type in ("FunctionDef", "Lambda", "ClassDef"))
            or (node_type, attr)
            in (
                ("TypeVar", "default_value"),
                ("TypeVarTuple", "default_value"),
                ("ParamSpec", "default_value"),
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
            ("TypeVar", "default_value"),
            ("TypeVarTuple", "default_value"),
            ("ParamSpec", "default_value"),
        ):
            ctx.in_async_context = False
        elif py314plus and (node_type, attr) == ("AnnAssign", "annotation"):
            # PEP 649 (3.14+): AnnAssign.annotation is a lazy code object,
            # not evaluated in the surrounding async scope.
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
        # Note: only clear on .body entry, not on decorator_list/args/returns which are
        # evaluated in the outer (class) scope, not the function scope.
        if attr == "body" and node_type == "ClassDef":
            ctx.in_class_not_function = True
        elif attr == "body" and is_function_def:
            ctx.in_class_not_function = False

        # --- in_annotation_scope: broad set of annotation-like positions —
        #     ClassDef.bases/keywords, returns, arg.annotation, TypeAlias.value,
        #     TypeVar.bound, and type-param default_value (3.13+).
        #     This is a superset of in_annotation_return_scope and in_type_scope.
        #     Rules should prefer the narrower flags rather than this broad flag. ---
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
        elif (node_type, attr) in (
            ("GeneratorExp", "elt"),
            ("ListComp", "elt"),
            ("SetComp", "elt"),
            ("DictComp", "key"),
            ("DictComp", "value"),
        ) or (
            attr == "body"
            and node_type
            in (
                "FunctionDef",
                "AsyncFunctionDef",
                "Lambda",
                "ClassDef",
            )
        ):
            # All comprehensions create their own implicit function scope, so
            # annotation-scope restrictions from the surrounding code do not apply
            # inside their body (elt/key/value).
            ctx.in_annotation_scope = False

        # --- in_ann_assign_annotation: inside AnnAssign.annotation ---
        if node_type == "AnnAssign" and attr == "annotation":
            ctx.in_ann_assign_annotation = True
        elif (node_type, attr) in (
            ("GeneratorExp", "elt"),
            ("ListComp", "elt"),
            ("SetComp", "elt"),
            ("DictComp", "key"),
            ("DictComp", "value"),
        ) or (
            attr == "body"
            and node_type
            in (
                "FunctionDef",
                "AsyncFunctionDef",
                "Lambda",
            )
        ):
            ctx.in_ann_assign_annotation = False

        # --- in_type_alias_in_class: inside TypeAlias.value when also inside ClassDef.body ---
        if node_type == "TypeAlias" and attr == "value" and ctx.in_class_not_function:
            ctx.in_type_alias_in_class = True
        elif is_function_def:
            ctx.in_type_alias_in_class = False

        # --- in_ann_assign_target: inside AnnAssign.target ---
        ctx.in_ann_assign_target = node_type == "AnnAssign" and attr == "target"
        # Since attr_order generates AnnAssign.value before AnnAssign.target,
        # node.node.value is already set at this point.  Capture it so the
        # subscript-slice check below can allow Starred when value is present.
        if node_type == "AnnAssign" and attr == "target":
            ctx.ann_assign_has_value = getattr(node.node, "value", None) is not None

        # --- in_ann_assign_subscript_slice: inside the slice of a Subscript that is
        #     the AnnAssign.target.  Starred in a subscript slice is a SyntaxError on
        #     py311+ ONLY when the AnnAssign has no value (e.g. `a[*x,]: T` is invalid
        #     but `a[*x,]: T = v` compiles fine).  The flag is transparent through
        #     Tuple.elts / List.elts within the slice, but is cleared when a nested
        #     Subscript is encountered (that nested subscript is in Load context and its
        #     slice can freely contain Starred). ---
        if (node_type, attr) == ("Subscript", "slice") and context.in_ann_assign_target:
            # Restrict Starred only when the AnnAssign has no value.
            ctx.in_ann_assign_subscript_slice = not context.ann_assign_has_value
        elif (
            context.in_ann_assign_subscript_slice
            and node_type in ("Tuple", "List")
            and attr == "elts"
        ):
            pass  # transparent through Tuple/List elts within the slice
        else:
            ctx.in_ann_assign_subscript_slice = False

        # --- in_delete_target: inside Delete.targets, cleared once inside sub-expression ---
        if node_type == "Delete" and attr == "targets":
            ctx.in_delete_target = True
        elif ctx.in_delete_target and (node_type, attr) in (
            ("Subscript", "value"),
            ("Subscript", "slice"),
            ("Attribute", "value"),
        ):
            ctx.in_delete_target = False

        # --- in_type_scope: inside TypeAlias.value or TypeVar.bound or type_param default_value ---
        if (node_type, attr) in (
            ("TypeAlias", "value"),
            ("TypeVar", "bound"),
            # py3.13+: default_value has the same walrus/yield/await restrictions
            ("TypeVar", "default_value"),
            ("TypeVarTuple", "default_value"),
            ("ParamSpec", "default_value"),
        ):
            ctx.in_type_scope = True
        elif (node_type, attr) == ("GeneratorExp", "elt") or (
            attr == "body"
            and node_type
            in (
                "FunctionDef",
                "AsyncFunctionDef",
                "Lambda",
                "ClassDef",
            )
        ):
            ctx.in_type_scope = False

        # --- in_comprehension_in_type_scope: inside a comprehension that is nested inside a
        #     type scope (without an intervening function/class boundary).
        #     Walrus (:=) escapes comprehension scopes to the nearest enclosing non-comprehension
        #     scope; if that scope is a type scope (no function frame), it is a SyntaxError.
        #     Unlike in_type_scope, this flag is NOT cleared when entering GeneratorExp.elt,
        #     because walrus would still try to escape to the outer type scope.
        #     It IS cleared at function/lambda/class body boundaries. ---
        if node_type in comprehensions and (
            context.in_type_scope or context.in_comprehension_in_type_scope
        ):
            ctx.in_comprehension_in_type_scope = True
        elif is_function_def or node_type == "ClassDef":
            ctx.in_comprehension_in_type_scope = False

        # --- in_comprehension_in_ann_assign_annotation: inside a SetComp/ListComp/DictComp
        #     nested inside AnnAssign.annotation (without an intervening function/class/
        #     GeneratorExp boundary).  On py314+ the annotation is a non-async code object,
        #     so await inside a set/list/dict comprehension there raises "asynchronous
        #     comprehension outside of an asynchronous function".
        #     GeneratorExp is excluded: (await x for x in y) is an async generator
        #     expression, valid to create in any context (it is lazy). ---
        if node_type in ("SetComp", "ListComp", "DictComp") and (
            context.in_ann_assign_annotation
            or context.in_comprehension_in_ann_assign_annotation
        ):
            ctx.in_comprehension_in_ann_assign_annotation = True
        elif is_function_def or node_type in ("ClassDef", "GeneratorExp"):
            ctx.in_comprehension_in_ann_assign_annotation = False

        # --- in_comprehension_in_annotation_return_scope: inside a SetComp/ListComp/DictComp
        #     nested inside an annotation-return-scope position (arg.annotation,
        #     FunctionDef.returns, AsyncFunctionDef.returns) without an intervening
        #     function/class/GeneratorExp boundary.  Same reasoning as
        #     in_comprehension_in_ann_assign_annotation. ---
        if node_type in ("SetComp", "ListComp", "DictComp") and (
            context.in_annotation_return_scope
            or context.in_comprehension_in_annotation_return_scope
        ):
            ctx.in_comprehension_in_annotation_return_scope = True
        elif is_function_def or node_type in ("ClassDef", "GeneratorExp"):
            ctx.in_comprehension_in_annotation_return_scope = False

        # --- in_annotation_return_scope: subset of in_annotation_scope covering only the three positions
        #     that PEP 649 (3.14+) makes lazily-evaluated code objects: arg.annotation,
        #     FunctionDef.returns, AsyncFunctionDef.returns.  The walrus operator := becomes a
        #     SyntaxError specifically in these positions in 3.14+, while it is still valid in
        #     ClassDef.bases/keywords (eagerly evaluated) even though those are also annotation scopes. ---
        if (node_type, attr) in (
            ("arg", "annotation"),
            ("FunctionDef", "returns"),
            ("AsyncFunctionDef", "returns"),
        ):
            ctx.in_annotation_return_scope = True
        elif (node_type, attr) in (
            ("GeneratorExp", "elt"),
            ("ListComp", "elt"),
            ("SetComp", "elt"),
            ("DictComp", "key"),
            ("DictComp", "value"),
        ) or (
            attr == "body"
            and node_type
            in (
                "FunctionDef",
                "AsyncFunctionDef",
                "Lambda",
                "ClassDef",
            )
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

        # type_comment fields are not preserved by ast.unparse (they are silently
        # dropped).  Any non-None value therefore makes the AST not round-trip
        # through unparse → parse, so we always force them to None.
        if hasattr(node, "type_comment"):
            setattr(node, "type_comment", None)

        if self.use(
            py310plus
            and isinstance(node, ast.withitem)
            and isinstance(node.context_expr, ast.Tuple)
            and bool(node.context_expr.elts)
        ):
            # Python 3.10+ treats `with (a, b):` as multiple context managers,
            # so ast.unparse of withitem(context_expr=Tuple([a, b])) produces
            # `with a, b:` which parses back as two separate withitems — the
            # Tuple wrapper is lost.  Replace with the first element so the
            # generated tree always round-trips.
            # Use a loop because elts[0] may itself be a Tuple (e.g. when the
            # generator produced a nested Tuple expression at this position).
            # Stop before unwrapping to a Starred: Tuple([*x]) unparses as
            # `(*x,)`, which round-trips correctly as a single-element tuple
            # context manager.  Starred is forbidden directly in context_expr,
            # so we must keep the Tuple wrapper in that case.
            while (
                isinstance(node.context_expr, ast.Tuple)
                and node.context_expr.elts
                and not isinstance(node.context_expr.elts[0], ast.Starred)
            ):
                node.context_expr = node.context_expr.elts[0]

        if self.use(hasattr(ast, "ExtSlice") and isinstance(node, ast.ExtSlice)):
            # ExtSlice only round-trips when it has ≥2 dims AND at least one is a
            # Slice.  ast.parse(ast.unparse(…)) otherwise returns a different node
            # type:
            #   ExtSlice([Index(e)])        → unparse "a[e]"     → parse Index(e)
            #   ExtSlice([Slice(a,b)])      → unparse "a[a:b]"   → parse Slice(a,b)
            #   ExtSlice([Index(x),Index(y)])→ unparse "a[x, y]" → parse Index(Tuple)
            # Normalise to the canonical form so the generator never emits a tree
            # that does_compile would reject for this reason, and the checker
            # correctly marks such trees as invalid.
            dims = node.dims  # type: ignore[union-attr]
            # A dim may be Index, Slice, or (illegally) a nested ExtSlice.
            # Only consider dims that are all ast.Index as "collapsible"; any
            # Slice or nested ExtSlice means we must keep the outer ExtSlice.
            all_index = all(isinstance(d, ast.Index) for d in dims)
            if len(dims) <= 1:
                # 0 dims: keep as Index(Tuple([])) → a[()]
                # 1 dim : unwrap the ExtSlice wrapper entirely
                if len(dims) == 0:
                    return ast.Index(value=ast.Tuple(elts=[], ctx=ast.Load()))  # type: ignore[attr-defined]
                return dims[0]  # Slice(…) or Index(e)
            if all_index:
                # ≥2 all-Index dims: ast.parse("a[x, y]") → Index(Tuple([x, y]))
                return ast.Index(  # type: ignore[attr-defined]
                    value=ast.Tuple(
                        elts=[d.value for d in dims],  # type: ignore[union-attr]
                        ctx=ast.Load(),
                    )
                )
            # ≥2 dims with at least one Slice (or nested ExtSlice): keep as-is.

        if isinstance(node, ast.ImportFrom):
            if self.use(node.level is None):
                # ast.parse always sets level to an int (never None); normalize
                # so the tree is stable after an unparse→parse round-trip.
                node.level = 0

            if self.use(
                node.module is None and (node.level is None or node.level == 0)
            ):
                node.level = 1

        if isinstance(node, ast.ExceptHandler):
            if self.use(node.type is None):
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

        if self.use(
            isinstance(node, ast.AnnAssign) and not isinstance(node.target, ast.Name)
        ):
            node.simple = 0

        if self.use(isinstance(node, ast.AnnAssign)):
            # ast.parse always sets simple to 0 or 1; normalize arbitrary ints
            # so the tree is stable after an unparse→parse round-trip.
            node.simple = int(bool(node.simple))

        if isinstance(node, ast.Constant):
            # TODO: what is Constant.kind
            # Constant.kind can be u for unicode strings
            allowed_kind: list[str | None] = [None]
            if isinstance(node.value, str):
                allowed_kind.append("u")
            if node.kind not in allowed_kind:
                node.kind = allowed_kind[hash(node.kind) % len(allowed_kind)]

            if self.use(
                not py312plus
                and context.fstring_value_depth > 0
                and isinstance(node.value, bytes)
                and "\\" in repr(node.value)
            ):
                # On <3.12, backslashes are forbidden inside f-string expression
                # parts ({...}).  ast.unparse renders bytes constants via repr(),
                # which uses backslash escape sequences for non-printable or
                # non-ASCII bytes (e.g. b'\x00' → b'\x00').  Such a constant
                # inside a FormattedValue.value would produce e.g. f"{b'\x00'!s}"
                # which is a SyntaxError on <3.12.  Replace with a safe bytes
                # value whose repr() contains no backslash.
                node.value = b" "

            if self.use(
                not py312plus
                and context.fstring_value_depth > 0
                and isinstance(node.value, str)
                and "\\" in repr(node.value)
            ):
                # Same as the bytes case above, but for str constants.
                # ast.unparse renders str constants via their repr, using
                # backslash escape sequences for characters like \, \n, \t,
                # \x00, etc. (e.g. '\\' → '\\\\', '\n' → '\\n').  A string
                # constant with such a value inside a FormattedValue.value
                # produces e.g. f"{'\\\\' !s}" which is a SyntaxError on <3.12.
                # Replace with a safe string whose repr() contains no backslash.
                node.value = " "

            if self.use(
                (
                    p_info == ("JoinedStr", "values")
                    or p_info == ("TemplateStr", "values")
                )
                and not isinstance(node.value, str)
            ):
                # TODO: better format string generation
                node.value = str(node.value)

            if self.use(
                # On 3.12.0–3.12.2, ast.unparse does not double-escape
                # backslashes inside format_spec constants: `\n` is emitted
                # as `\n` (a newline after parsing) rather than `\\n`.
                # The only safe backslash in a format_spec is a single
                # trailing one (e.g. `f'{x:\}'`) which Python leaves as a
                # literal `\}` terminator.  Strip all other backslashes.
                py312plus
                and not py1223plus  # 3.12.0–3.12.2 only (3.8 handled by the block below)
                and (
                    p_info == ("JoinedStr", "values")
                    or p_info == ("TemplateStr", "values")
                )
                and parent_node.parent.parent_attr == "format_spec"
                and isinstance(node.value, str)
                and "\\" in node.value
                and not (
                    node.value.endswith("\\") and not node.value[:-1].endswith("\\")
                )
            ):
                node.value = node.value.replace("\\", "")

            if self.use(
                (
                    p_info == ("JoinedStr", "values")
                    or p_info == ("TemplateStr", "values")
                )
                and isinstance(node.value, str)
                and "'" in node.value
                and '"' in node.value
                and not py39plus
                and '"""' not in node.value
                and not any(
                    isinstance(v, ast.FormattedValue)
                    for v in parent_node.parent.node.values  # type: ignore[union-attr]
                )
            ):
                # On <3.9 (astunparse): when content has BOTH ' and " but no
                # """, astunparse uses triple-double-quoted outer form
                # (f"""...""").  If the content ends with 1 or 2 " chars
                # those merge with the closing """ → SyntaxError.
                # Strip only trailing " so e.g. "'" stays intact.
                # (When content has """, astunparse switches to triple-SINGLE-
                # quote form which handles """ correctly — no stripping needed.)
                node.value = node.value.rstrip('"')

            if self.use(
                (
                    p_info == ("JoinedStr", "values")
                    or p_info == ("TemplateStr", "values")
                )
                and isinstance(node.value, str)
                and "'''" in node.value
                and '"""' in node.value
                and (
                    # Case A: this constant is a direct literal sibling of a
                    # FormattedValue in the outer JoinedStr.  On Python <3.9.1
                    # (astunparse on 3.8 and the initial 3.9.0 release),
                    # escape-sequence mode (triggered by ''' + """) can
                    # backslash-escape the quotes of a nested JoinedStr
                    # (f-string) inside a sibling FormattedValue's expression,
                    # producing \' inside {…} which Python rejects as
                    # "f-string expression part cannot include a backslash".
                    # Only strip """ when a sibling FV actually contains a
                    # nested JoinedStr — plain expressions (Dict, Name, …)
                    # have no quote characters to escape.  Fixed in 3.9.1.
                    (
                        not py391plus
                        and any(
                            isinstance(v, ast.FormattedValue)
                            and any(
                                isinstance(n, ast.JoinedStr)
                                for n in ast.walk(v.value)
                            )
                            for v in parent_node.parent.node.values  # type: ignore[union-attr]
                        )
                    )
                    # Case B: this constant is in a format_spec JoinedStr.
                    # astunparse (3.8) and Python 3.9–3.12.2's ast.unparse
                    # both fail when format_spec content has ''' + """: the
                    # outer JoinedStr ends up in escape-sequence mode (3.8) or
                    # ast.unparse raises "Unable to avoid backslash" (3.9–3.11)
                    # or generates uncompilable source (3.12.0–3.12.2, fixed
                    # in 3.12.3).
                    or (
                        not py1223plus
                        and parent_node.parent.parent_attr == "format_spec"  # type: ignore[union-attr]
                    )
                )
            ):
                # Remove all """ sequences so the value can be represented
                # without escape-sequence mode, e.g. '''""" → ''' → the outer
                # f-string can use double-quote form (f"'''") without escaping.
                node.value = node.value.replace('"""', "")

            if self.use(
                not py312plus
                and (
                    p_info == ("JoinedStr", "values")
                    or p_info == ("TemplateStr", "values")
                )
                and isinstance(node.value, str)
                and "\\" in node.value
                and (
                    # On <3.9 (astunparse), backslashes in f-string literal
                    # constants cause problems.  Strip them UNLESS one of these
                    # safe cases applies:
                    #   (a) the value contains BOTH ''' and """ — astunparse
                    #       uses escape-sequence mode (single-quote outer with
                    #       \' and \\), which handles backslashes correctly.
                    #       NOTE: this block runs AFTER the """ strip block above,
                    #       so if """ was stripped, this exception no longer applies
                    #       and the backslash will correctly be stripped here.
                    #   (b) the constant is in a format_spec JoinedStr AND
                    #       the value ends with exactly one backslash — e.g.
                    #       `f'{x!s:\}'` round-trips fine (the trailing `\`
                    #       before `}` is literal in format specs).  Two or
                    #       more trailing backslashes fail because `\\` is
                    #       interpreted as one backslash by the parser.
                    (
                        not py39plus
                        and not ("'''" in node.value and '"""' in node.value)
                        and not (
                            parent_node.parent.parent_attr == "format_spec"
                            and node.value.endswith("\\")
                            and not node.value[:-1].endswith("\\")
                        )
                        and not (
                            # A trailing lone backslash immediately before a
                            # FormattedValue sibling is safe: astunparse emits
                            # f'...\{expr}' where \{ on Python <3.12 is treated
                            # as a literal backslash and round-trips correctly.
                            # However this only holds when the prefix (the
                            # value without the trailing \) itself contains no
                            # backslash.  If it does, astunparse enters
                            # escape-sequence mode for the earlier \ chars
                            # (e.g. \' → escape for apostrophe) and the
                            # trailing \ is then emitted raw instead of as
                            # \\, breaking the round-trip (e.g. \'\  →
                            # f"\'\{x}" → re-parse gives '\ not \'\).
                            node.value.endswith("\\")
                            and not node.value[:-1].endswith("\\")
                            and "\\" not in node.value[:-1]
                            and parent_node.parent_attr_index is not None
                            and parent_node.parent_attr_index + 1
                            < len(parent_node.parent.node.values)  # type: ignore[union-attr, arg-type]
                            and isinstance(
                                parent_node.parent.node.values[  # type: ignore[union-attr, index]
                                    parent_node.parent_attr_index + 1
                                ],
                                ast.FormattedValue,
                            )
                        )
                    )
                    # On 3.9–3.11, backslashes inside the *expression* part of
                    # an f-string (`{...}`) are forbidden.  When this JoinedStr
                    # is nested inside a FormattedValue.value, the backslash
                    # ends up in the expression part of the outer f-string and
                    # ast.unparse raises ValueError('Unable to avoid backslash
                    # in f-string expression part').
                    # fstring_value_depth > 0 means we are inside at least one
                    # FormattedValue.value chain.
                    or context.fstring_value_depth > 0
                )
            ):
                # Strip backslashes so the tree is always representable.
                # An empty result is handled by the next (empty → " ") block.
                node.value = node.value.replace("\\", "")

            if self.use(
                (
                    p_info == ("JoinedStr", "values")
                    or p_info == ("TemplateStr", "values")
                )
                and node.value == ""
            ):
                # An empty-string Constant inside a JoinedStr/TemplateStr is
                # silently dropped by ast.parse(ast.unparse(...)), so it does
                # not round-trip.  Replace it with a single space.
                node.value = " "

            if self.use(
                (
                    p_info == ("JoinedStr", "values")
                    or p_info == ("TemplateStr", "values")
                )
                and node.kind is not None
            ):
                # ast.parse always produces kind=None for Constant parts inside
                # a JoinedStr/TemplateStr; the kind is lost on unparse→parse.
                node.kind = None

        if self.use(
            isinstance(node, ast.JoinedStr)
            or (sys.version_info >= (3, 14) and isinstance(node, ast.TemplateStr))
        ):
            # CPython's parser merges adjacent Constant string parts when
            # round-tripping through unparse→parse (e.g. [Const("'"), Const("'")]
            # becomes [Const("''")]).  Pre-merge them here so the tree is stable.
            new_values: list[ast.expr] = []
            for v in node.values:
                if (
                    new_values
                    and isinstance(new_values[-1], ast.Constant)
                    and isinstance(v, ast.Constant)
                    and isinstance(new_values[-1].value, str)
                    and isinstance(v.value, str)
                ):
                    new_values[-1].value += v.value  # type: ignore[union-attr]
                else:
                    new_values.append(v)
            node.values = new_values
            # After merging, the combined string values may have new problematic
            # combinations (e.g. one constant ends with "" and the next starts
            # with '"' creating a new '"""' sequence, or a merged value has both
            # ''' and """ which would enable escape-sequence mode in astunparse
            # — and then a subsequent strip of """ would leave a dangling \).
            # Re-apply the same strip logic that was applied to each constant
            # individually to ensure the final merged values are also clean.
            has_fv_sibling = any(
                isinstance(v, ast.FormattedValue)
                and any(isinstance(n, ast.JoinedStr) for n in ast.walk(v.value))
                for v in node.values
            )
            is_in_format_spec = parent_node.parent_attr == "format_spec"  # type: ignore[union-attr]
            for merged_idx, merged in enumerate(node.values):
                if not isinstance(merged, ast.Constant) or not isinstance(
                    merged.value, str
                ):
                    continue
                mv = merged.value
                # Re-apply """ strip
                if (
                    "'''" in mv
                    and '"""' in mv
                    and (
                        (not py391plus and has_fv_sibling)
                        or (not py1223plus and is_in_format_spec)
                    )
                ):
                    merged.value = mv = mv.replace('"""', "")
                # Re-apply backslash strip (runs AFTER """ strip so condition is correct)
                if (
                    not py312plus
                    and "\\" in mv
                    and (
                        (
                            not py39plus
                            and not ("'''" in mv and '"""' in mv)
                            and not (
                                is_in_format_spec
                                and mv.endswith("\\")
                                and not mv[:-1].endswith("\\")
                            )
                            and not (
                                mv.endswith("\\")
                                and not mv[:-1].endswith("\\")
                                and "\\" not in mv[:-1]
                                and merged_idx + 1 < len(node.values)
                                and isinstance(
                                    node.values[merged_idx + 1], ast.FormattedValue
                                )
                            )
                        )
                        or context.fstring_value_depth > 0
                    )
                ):
                    merged.value = mv = mv.replace("\\", "")

        if isinstance(node, InterpolationOrFormattedValue):
            valid_conversion = (-1, 115, 114, 97)
            if self.use(not py310plus and node.conversion is None):
                node.conversion = 5
            if self.use(node.conversion not in valid_conversion):
                # node.conversion may be None (on 3.10+ None is allowed by the
                # grammar but was not handled above) — treat None as 0 for the
                # modulo index.
                node.conversion = valid_conversion[(node.conversion or 0) % 4]

        if hasattr(node, "ctx"):
            if self.use(context.in_delete_target):
                node.ctx = ast.Del()
            elif self.use(context.in_store_target):
                node.ctx = ast.Store()
            else:
                node.ctx = ast.Load()

        if self.use(
            isinstance(node, (ast.List, ast.Tuple)) and isinstance(node.ctx, ast.Store)
        ):
            only_firstone(node.elts, lambda e: isinstance(e, ast.Starred))

        if self.use(
            isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef, ast.Lambda))
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

        if self.use(isinstance(node, ast.AsyncFunctionDef)):
            if any(
                isinstance(n, (ast.Yield, ast.YieldFrom))
                for n in walk_function_nodes(node.body)
            ):
                for n in walk_function_nodes(node.body):
                    if isinstance(n, ast.Return):
                        n.value = None

        if self.use(isinstance(node, (ast.ClassDef, ast.Call))):
            # unique keyword names
            seen = set()
            for i, kw in reversed(list(enumerate(node.keywords))):
                if kw.arg:
                    if kw.arg in seen:
                        del node.keywords[i]
                    seen.add(kw.arg)

        if self.use(isinstance(node, ast.Try)):
            node.handlers[:-1] = [
                handler for handler in node.handlers[:-1] if handler.type is not None
            ]
            if self.use(not node.handlers):
                node.orelse = []

        if self.use(
            isinstance(
                node, (ast.GeneratorExp, ast.ListComp, ast.DictComp, ast.SetComp)
            )
        ):
            # SyntaxError: assignment expression cannot rebind comprehension iteration variable 'name_3'
            # Guard against None targets/iters: these can occur when an
            # invalid_option path generates a comprehension in a context where
            # all store-target options are simultaneously forbidden (e.g. inside
            # MatchValue + UnaryOp), leaving the field unset (None).
            names = {
                n.id
                for c in node.generators
                if c.target is not None
                for n in ast.walk(c.target)
                if isinstance(n, ast.Name)
            } | {
                n.id
                for c in node.generators
                if c.iter is not None
                for n in ast.walk(c.iter)
                if isinstance(n, ast.Name)
            }
            use = self.use

            class Transformer(ast.NodeTransformer):
                def visit_NamedExpr(
                    self, node: ast.NamedExpr
                ) -> ast.AST | list[ast.AST] | None:
                    if use(node.target.id in names):
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

        if isinstance(node, ast.comprehension):
            # is_async is logically boolean (0 = sync, 1 = async).  Any truthy
            # value other than 1 (e.g. 2) compiles identically but does not
            # round-trip through ast.unparse→ast.parse (always produces 1).
            node.is_async = int(bool(node.is_async))

        if isinstance(node, (ast.ListComp, ast.SetComp, ast.DictComp)):
            if self.use(not context.in_async_context):
                for comp in node.generators:
                    comp.is_async = 0

        if isinstance(node, ast.Raise):
            if self.use(not node.exc):
                node.cause = None

        if self.use(isinstance(node, ast.Lambda)):
            # no annotation for lambda arguments
            for args in all_args(node.args):
                for arg in args:
                    arg.annotation = None

            if self.use(node.args.vararg is not None):
                node.args.vararg.annotation = None

            if self.use(node.args.kwarg is not None):
                node.args.kwarg.annotation = None

        if self.use(
            isinstance(node, InterpolationOrFormattedValue)
            and isinstance(node.format_spec, ast.JoinedStr)
        ):
            for const in node.format_spec.values:
                if isinstance(const, ast.Constant):
                    assert isinstance(const.value, str)
                    const.value = const.value.replace("{", "").replace("}", "")

        if sys.version_info >= (3, 12):

            use = self.use
            # type scopes
            if self.use(hasattr(node, "type_params")):
                node.type_params = unique_by(node.type_params, lambda p: p.name)

            def cleanup_annotation(
                annotation: ast.expr,
                stop_at_inner_scopes: bool = False,
            ) -> ast.expr:
                """Remove invalid constructs (walrus, yield, await) from an annotation.

                ``stop_at_inner_scopes=True`` prevents recursion into comprehension
                bodies (ListComp/SetComp/DictComp/GeneratorExp) and Lambda bodies.
                Use this for annotation positions (e.g. AnnAssign.annotation on
                3.14+) where walrus *inside* a comprehension or lambda is still
                valid because those inner scopes have their own function frame.
                Leave ``stop_at_inner_scopes=False`` for type-scope positions
                (TypeVar.bound, TypeAlias.value, generic-function annotations) where
                walrus is invalid even inside nested comprehensions.
                """

                class Transformer(ast.NodeTransformer):
                    if stop_at_inner_scopes:
                        # Comprehensions and lambdas create their own implicit
                        # function scope, so walrus/yield/await inside them is
                        # valid in 3.14+ annotation contexts.  Stop recursion.
                        def visit_ListComp(
                            self, node: ast.ListComp
                        ) -> ast.AST | list[ast.AST] | None:
                            return node

                        def visit_SetComp(
                            self, node: ast.SetComp
                        ) -> ast.AST | list[ast.AST] | None:
                            return node

                        def visit_DictComp(
                            self, node: ast.DictComp
                        ) -> ast.AST | list[ast.AST] | None:
                            return node

                        def visit_GeneratorExp(
                            self, node: ast.GeneratorExp
                        ) -> ast.AST | list[ast.AST] | None:
                            return node

                        def visit_Lambda(
                            self, node: ast.Lambda
                        ) -> ast.AST | list[ast.AST] | None:
                            return node

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

                    def visit_Await(
                        self, node: ast.Await
                    ) -> ast.AST | list[ast.AST] | None:
                        if not use():
                            return self.generic_visit(node)
                        return self.visit(node.value)

                return Transformer().visit(annotation)  # type: ignore[return-value]

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
                    if self.use(
                        func_arg is not None and func_arg.annotation is not None
                    ):
                        func_arg.annotation = cleanup_annotation(func_arg.annotation)

                if self.use(node.returns is not None):
                    node.returns = cleanup_annotation(node.returns)

            if isinstance(node, ast.ClassDef) and node.type_params:
                node.bases = [cleanup_annotation(b) for b in node.bases]
                for kw in node.keywords:
                    if self.use():
                        kw.value = cleanup_annotation(kw.value)

                for n in ast.walk(node):
                    if self.use(isinstance(n, ast.TypeAlias)):
                        n.value = cleanup_annotation(n.value)

            if isinstance(node, ast.ClassDef):
                for n in ast.walk(node):
                    if self.use(isinstance(n, ast.TypeVar) and n.bound is not None):
                        n.bound = cleanup_annotation(n.bound)

            if self.use(isinstance(node, ast.AnnAssign)):
                if py314plus:
                    # PEP 649 (3.14+): walrus/yield/await at the top level of
                    # AnnAssign.annotation are now invalid (lazy code object).
                    # However, walrus/yield/await inside a comprehension or lambda
                    # body remain valid because those inner scopes have their own
                    # implicit function frame.  Use stop_at_inner_scopes=True so
                    # cleanup_annotation does not descend into those boundaries.
                    node.annotation = cleanup_annotation(
                        node.annotation, stop_at_inner_scopes=True
                    )
                # else (3.12/3.13): walrus/yield/await are valid everywhere in
                # AnnAssign.annotation — no cleanup needed.

        if sys.version_info >= (3, 13):
            if hasattr(node, "type_params"):
                # non-default type parameter 'name_1' follows default type parameter
                # All default params must come at the end: clear defaults from any
                # param that appears (in forward order) before a non-default param.
                no_default_seen = False
                for child in reversed(node.type_params):
                    if child.default_value is None:
                        no_default_seen = True
                    elif self.use(no_default_seen):
                        child.default_value = None

        return node

    def fix_result(self, node: ast.AST) -> ast.AST:
        if sys.version_info >= (3, 14):
            for n in walk_childs_first(node):
                if self.use(isinstance(n, ast.Interpolation)):
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

                if self.use(
                    isinstance(n, ast.Interpolation)
                    and n.format_spec is not None
                    and n.conversion == -1
                    and isinstance(n.str, str)
                    and "!" in n.str
                ):
                    # CPython parser bug: when the expression text contains '!'
                    # (only possible via '!=' / NotEq) AND a format_spec is
                    # present AND there is no conversion flag, the parser
                    # misidentifies '!' as the start of a conversion flag and
                    # truncates 'str' at '!'.  Removing format_spec avoids the
                    # round-trip failure (t'{0 != 0}' round-trips correctly).
                    n.format_spec = None

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
                ]
                if not py314plus:
                    # On 3.14+, returns and arg.annotation are lazy code objects
                    # (PEP 649): names there are NOT "used" for global/nonlocal.
                    all_nodes.append(node.returns)
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
                ]
                if not py314plus:
                    # On 3.14+, returns and arg.annotation are lazy code objects
                    # (PEP 649): names there are NOT "used" for global/nonlocal.
                    all_nodes.append(node.returns)
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
            return 2
        if node_type == "Set" and attr_name == "elts":
            # An empty set literal does not exist in Python syntax: {} parses as a
            # dict, so Set.elts must always have at least one element.
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
        # Python 3.15+ marks DictComp.value as optional in the grammar, but ast.unparse
        # does not handle DictComp(value=None) and raises AttributeError.  Forbid None
        # here so neither the generator nor the checker ever produces such a tree.
        if (
            child.parent_attr == "value"
            and type(child.parent.node).__name__ == "DictComp"  # type: ignore[union-attr]
        ):
            return False
        return True

    def attr_order(self, ast_type_name: str, field_names: list[str]) -> list[str]:
        if ast_type_name == "AnnAssign":
            # Generate 'value' before 'target' so that context_before for
            # AnnAssign.target can inspect node.node.value and know whether
            # Starred in a subscript slice is valid (it is when value is not None).
            result = [n for n in field_names if n != "value"]
            result.insert(result.index("target"), "value")
            return result
        return field_names

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
