from __future__ import annotations

import ast
import itertools
import sys
from dataclasses import replace
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
        parents = node.all_parents()
        parent_types = [p[0] for p in parents]

        def inside(
            types: str | tuple[str, ...], not_types: tuple[str, ...] = ()
        ) -> bool:
            if not isinstance(types, tuple):
                types = (types,)

            for parent, arg in reversed(parents):
                qual_parent = f"{parent}.{arg}"
                if any(qual_parent == t if "." in t else parent == t for t in types):
                    return True
                if any(
                    qual_parent == t if "." in t else parent == t for t in not_types
                ):
                    return False
            return False

        if child_name in ("Store", "Del", "Load"):
            return 1

        if child_name == "Slice" and not (
            parents[-1] == ("Subscript", "slice")
            or parents[-2:]
            == [
                ("Subscript", "slice"),
                ("Tuple", "elts"),
            ]
        ):
            raise Invalid

        if child_name == "ExtSlice" and parents[-1] == ("ExtSlice", "dims"):
            # SystemError('extended slice invalid in nested slice')
            raise Invalid

        # f-string
        if parents[-1] == ("JoinedStr", "values") and child_name not in (
            "Constant",
            "FormattedValue",
        ):
            raise Invalid

        if 0:
            if (
                not py312plus
                and parents[-1] == ("FormattedValue", "value")
                and child_name != "Constant"
            ):
                # TODO: WHY?
                raise Invalid

        if (
            parents[-1] == ("FormattedValue", "format_spec")
            and child_name != "JoinedStr"
        ):
            raise Invalid

        if (
            child_name == "JoinedStr"
            and parents.count(("FormattedValue", "format_spec")) > f_string_format_limit
        ):
            raise Invalid

        if (
            child_name == "JoinedStr"
            and parents.count(("FormattedValue", "value")) > f_string_expr_limit
        ):
            raise Invalid

        if child_name == "FormattedValue" and parents[-1][0] != "JoinedStr":
            # TODO: doc says this should be valid, maybe a bug in the python doc
            # see https://github.com/python/cpython/issues/111257
            raise Invalid

        if inside(
            ("Delete.targets"),
            ("Subscript.value", "Subscript.slice", "Attribute.value"),
        ) and child_name not in (
            "Name",
            "Attribute",
            "Subscript",
            "List",
            "Tuple",
        ):
            raise Invalid

        # function statements
        if child_name in (
            "Return",
            "Yield",
            "YieldFrom",
        ) and not inside(
            ("FunctionDef.body", "AsyncFunctionDef.body", "Lambda.body"),
            ("ClassDef.body",),
        ):
            raise Invalid
        # function statements
        if child_name in ("Nonlocal",) and not inside(
            (
                "FunctionDef.body",
                "AsyncFunctionDef.body",
                "Lambda.body",
                "ClassDef.body",
            )
        ):
            raise Invalid

        if (
            not py38plus
            and child_name == "Continue"
            and inside(
                ("Try.finalbody", "TryStar.finalbody"),
                ("FunctionDef.body", "AsyncFunctionDef.body"),
            )
        ):
            raise Invalid

        if parents[-1] == ("MatchMapping", "keys") and child_name != "Constant":
            # TODO: find all allowed key types
            raise Invalid

        if child_name == "MatchStar" and parent_types[-1] != "MatchSequence":
            raise Invalid

        if child_name == "Starred" and parents[-1] not in (
            ("Tuple", "elts"),
            ("Call", "args"),
            ("List", "elts"),
            ("Set", "elts"),
            ("ClassDef", "bases"),
        ):
            raise Invalid

        assign_target = ("Subscript", "Attribute", "Name", "Starred", "List", "Tuple")

        assign_context = [
            p for p in parents if p[0] not in ("Tuple", "List", "Starred")
        ]

        if assign_context and assign_context[-1] in [
            ("For", "target"),
            ("AsyncFor", "target"),
            ("AnnAssign", "target"),
            ("AugAssign", "target"),
            ("Assign", "targets"),
            ("withitem", "optional_vars"),
            ("comprehension", "target"),
        ]:
            if child_name not in assign_target:
                raise Invalid

        if parents[-1] in [("AugAssign", "target"), ("AnnAssign", "target")]:
            if child_name in ("Starred", "List", "Tuple"):
                raise Invalid

        if inside(("AnnAssign.target",)) and child_name == "Starred":
            # TODO this might be a cpython bug
            raise Invalid

        if parents[-1] in [("AnnAssign", "target")]:
            if child_name not in ("Name", "Attribute", "Subscript"):
                raise Invalid

        if parents[-1] in [("NamedExpr", "target")] and child_name != "Name":
            raise Invalid

        if (
            child_name in ("AsyncFor", "Await", "AsyncWith")
            and not context.in_async_code
        ):
            raise Invalid

        if child_name in ("YieldFrom",) and context.in_async_code:
            raise Invalid

        if child_name in ("Break", "Continue") and not context.in_loop:
            raise Invalid

        if inside("TryStar.handlers") and child_name in ("Break", "Continue", "Return"):
            # SyntaxError: 'break', 'continue' and 'return' cannot appear in an except* block
            raise Invalid

        if inside(("MatchValue",)) and child_name not in (
            "Attribute",
            "Name",
            "Constant",
            "UnaryOp",
            "USub",
        ):
            raise Invalid

        if (
            inside("MatchValue.value")
            and inside("Attribute.value")
            and child_name not in ("Attribute", "Name")
        ):
            raise Invalid

        if (
            inside(("MatchValue",))
            and inside(("UnaryOp",))
            and child_name in ("Name", "UnaryOp", "Attribute")
        ):
            raise Invalid

        if parents[-1] == ("MatchValue", "value") and child_name == "Name":
            raise Invalid

        if inside("MatchClass.cls"):
            if child_name not in ("Name", "Attribute"):
                raise Invalid

        if parents[-1] == ("comprehension", "iter") and child_name == "NamedExpr":
            raise Invalid

        if inside(comprehensions) and child_name in ("Yield", "YieldFrom"):
            # SyntaxError: 'yield' inside list comprehension
            raise Invalid

        if (
            inside(comprehensions)
            # TODO restrict to comprehension inside ClassDef
            and inside(
                "ClassDef.body",
                ("FunctionDef.body", "AsyncFunctionDef.body", "Lambda.body"),
            )
            and child_name == "NamedExpr"
        ):
            # SyntaxError: assignment expression within a comprehension cannot be used in a class body
            raise Invalid

        if not py39plus and any(p[1] == "decorator_list" for p in parents):
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
            if parents[-1] == ("TypeAlias", "name") and child_name != "Name":
                raise Invalid

            if (
                child_name == "Lambda"
                and inside("TypeAlias.value")
                and inside("ClassDef.body")
                and sys.version_info < (3, 13)
            ):
                # SyntaxError('Cannot use lambda in annotation scope within class scope')
                raise Invalid

            if child_name in (
                # "NamedExpr",
                "Yield",
                "YieldFrom",
                "Await",
                # "DictComp",
                # "ListComp",
                # "SetComp",
            ) and inside(
                (
                    "ClassDef.bases",
                    "ClassDef.keywords",
                    "FunctionDef.returns",
                    "AsyncFunctionDef.returns",
                    "arg.annotation",
                    "TypeAlias.value",
                    "TypeVar.bound",
                )
            ):
                # todo this should only be invalid in type scopes (when the class/def has type parameters)
                # and only for async comprehensions
                raise Invalid

            if child_name in ("NamedExpr",) and inside(
                ("TypeAlias.value", "TypeVar.bound")
            ):
                # todo this should only be invalid in type scopes (when the class/def has type parameters)
                # and only for async comprehensions
                raise Invalid

            if child_name == "Await" and inside("AnnAssign.annotation"):
                raise Invalid

            if sys.version_info < (3, 13):
                type_alias_context = ("AsyncFunctionDef", "ClassDef")
            else:
                type_alias_context = ("AsyncFunctionDef",)

            if (
                inside(("TypeAlias", "AnnAssign.annotation"))
                and inside(type_alias_context)
                and child_name in comprehensions
            ):
                raise Invalid

        if sys.version_info >= (3, 14):
            if child_name == "NamedExpr" and inside(
                (
                    "arg.annotation",
                    "FunctionDef.returns",
                    "AsyncFunctionDef.returns",
                )
            ):
                raise Invalid

            if not parent_types[-1] == "TemplateStr" and child_name == "Interpolation":
                raise Invalid

            if parents[-1] == ("TemplateStr", "values") and child_name not in (
                "Interpolation",
                "Constant",
            ):
                raise Invalid

            if (
                parents[-1] == ("Interpolation", "format_spec")
                and child_name != "JoinedStr"
            ):
                raise Invalid

        if child_name == "Expr":
            return 30

        if child_name == "NonLocal" and parents[-1] == ("Module", "body"):
            raise Invalid

        return 1

    def context_before(
        self, context: Context, node: NodeRef, attr: str, index: int | None
    ) -> Context:
        node_type = type(node.node).__name__

        # --- in_async_code: mirrors inside() in probability_try ---
        # AsyncFunctionDef.body and GeneratorExp.elt activate async context
        if (node_type, attr) in (("AsyncFunctionDef", "body"), ("GeneratorExp", "elt")):
            context = replace(context, in_async_code=True)
        # FunctionDef.body, Lambda.body, ClassDef.body reset it
        elif (node_type, attr) in (
            ("FunctionDef", "body"),
            ("Lambda", "body"),
            ("ClassDef", "body"),
        ):
            context = replace(context, in_async_code=False)

        # --- in_async_context: mirrors fix()'s in_async_code loop (stricter) ---
        # Only AsyncFunctionDef.body activates; annotations/type-params/nested fns reset
        if node_type == "AsyncFunctionDef" and attr == "body":
            context = replace(context, in_async_context=True)
        elif node_type in ("FunctionDef", "Lambda", "ClassDef", "TypeAlias"):
            context = replace(context, in_async_context=False)
        elif (node_type, attr) in (
            ("AsyncFunctionDef", "returns"),
            ("arg", "annotation"),
            ("TypeVar", "bound"),
        ):
            context = replace(context, in_async_context=False)
        elif not py311plus and node_type in comprehensions:
            context = replace(context, in_async_context=False)

        # --- in_loop: mirrors the inside() call in probability_try ---
        # Entering a loop body enables in_loop
        if (node_type, attr) in (
            ("For", "body"),
            ("While", "body"),
            ("AsyncFor", "body"),
        ):
            context = replace(context, in_loop=True)
        # Entering a function/class body resets in_loop
        elif (node_type, attr) in (
            ("FunctionDef", "body"),
            ("Lambda", "body"),
            ("AsyncFunctionDef", "body"),
            ("ClassDef", "body"),
        ):
            context = replace(context, in_loop=False)

        # --- in_excepthandler: mirrors the loop in fix() ---
        if node_type == "ExceptHandler":
            context = replace(context, in_excepthandler=True)
        elif node_type in ("FunctionDef", "Lambda", "AsyncFunctionDef"):
            context = replace(context, in_excepthandler=False)

        return context

    def fix(self, node: ast.AST, parent_node: NodeRef, context: Context) -> ast.AST:

        parents = parent_node.all_parents()

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
            and parents[-1] == ("Subscript", "slice")
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
                and parents
                and (
                    parents[-1] == ("JoinedStr", "values")
                    or parents[-1] == ("TemplateStr", "values")
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

        assign_context = [
            p for p in parents if p[0] not in ("Tuple", "List", "Starred")
        ]

        if hasattr(node, "ctx"):
            if (
                self.use()
                and assign_context
                and assign_context[-1] == ("Delete", "targets")
            ):
                node.ctx = ast.Del()
            elif (
                self.use()
                and assign_context
                and assign_context[-1]
                in (
                    ("Assign", "targets"),
                    ("AnnAssign", "target"),
                    ("AugAssign", "target"),
                    ("NamedExpr", "target"),
                    ("TypeAlias", "name"),
                    ("For", "target"),
                    ("AsyncFor", "target"),
                    ("withitem", "optional_vars"),
                    ("comprehension", "target"),
                )
            ):
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

            # @lambda f:lambda pattern:set(f(pattern))
            def all_names(node):
                if isinstance(node, ast.MatchAs) and node.name:
                    yield node.name
                elif isinstance(node, ast.MatchStar) and node.name:
                    yield node.name
                elif isinstance(node, ast.MatchMapping) and node.rest:
                    yield node.rest
                elif isinstance(node, ast.MatchOr):
                    yield from set.intersection(
                        *[set(all_names(pattern)) for pattern in node.patterns]
                    )
                else:
                    for child in ast.iter_child_nodes(node):
                        yield from all_names(child)

            class RemoveName(ast.NodeVisitor):
                def __init__(self, condition: Callable[[str | None], bool]) -> None:
                    self.condition = condition

                def visit_MatchAs(self, node: ast.MatchAs) -> None:
                    if self.condition(node.name):
                        node.name = None

                def visit_MatchMapping(self, node: ast.MatchMapping) -> None:
                    if self.condition(node.rest):
                        node.rest = None

            class RemoveNameCleanup(ast.NodeTransformer):
                def visit_MatchAs(
                    self, node: ast.MatchAs
                ) -> ast.AST | list[ast.AST] | None:
                    if node.name is None and node.pattern is not None:
                        return self.visit(node.pattern)
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

                def visit_MatchAs(
                    self, node: ast.MatchAs
                ) -> ast.AST | list[ast.AST] | None:
                    if not self.is_allowed(node.name):
                        return ast.MatchSingleton(value=None)
                    elif node.name is not None:
                        self.used.add(node.name)
                    return self.generic_visit(node)

                def visit_MatchStar(
                    self, node: ast.MatchStar
                ) -> ast.AST | list[ast.AST] | None:
                    if not self.is_allowed(node.name):
                        return ast.MatchSingleton(value=None)
                    elif node.name is not None:
                        self.used.add(node.name)
                    return self.generic_visit(node)

                def visit_MatchMapping(
                    self, node: ast.MatchMapping
                ) -> ast.AST | list[ast.AST] | None:
                    if not self.is_allowed(node.rest):
                        return ast.MatchSingleton(value=None)
                    elif node.rest is not None:
                        self.used.add(node.rest)
                    return self.generic_visit(node)

                def visit_MatchOr(self, node: ast.MatchOr) -> ast.MatchOr:
                    allowed = set.intersection(
                        *[set(all_names(pattern)) for pattern in node.patterns]
                    )
                    allowed -= self.used

                    node.patterns = [
                        FixPatternNames(set(self.used), allowed).visit(child)  # type: ignore[arg-type]
                        for child in node.patterns
                    ]

                    self.used |= allowed

                    return node

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
                no_default = False
                for child in reversed(node.type_params):
                    if child.default_value is not None:
                        no_default = True
                    if self.use() and no_default:
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
                if isinstance(node.target, ast.Name) and (
                    node.target.id in self.used_globals
                    or node.target.id in self.used_nonlocals
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

        fixer = NonLocalFixer([], [], [], [], [])
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

    def none_allowed(self, parent: NodeRef) -> bool:
        parents = parent.all_parents()
        if parents[-2:] == [("TryStar", "handlers"), ("ExceptHandler", "type")]:
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
