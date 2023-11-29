from __future__ import annotations

import ast
import inspect
import itertools
import re
import sys
from copy import deepcopy
from typing import Any

from .types import BuiltinNodeType
from .types import NodeType
from .types import UnionNodeType

if sys.version_info >= (3, 9):
    from ast import unparse
else:
    from astunparse import unparse  # type: ignore

from ._limits import f_string_format_limit, f_string_expr_limit

from ._utils import ast_dump

py38plus = (3, 8) <= sys.version_info
py39plus = (3, 9) <= sys.version_info
py310plus = (3, 10) <= sys.version_info
py311plus = (3, 11) <= sys.version_info
py312plus = (3, 12) <= sys.version_info

type_infos: dict[str, NodeType | BuiltinNodeType | UnionNodeType] = {}


def all_args(args):
    if py38plus:
        return (args.posonlyargs, args.args, args.kwonlyargs)
    else:
        return (args.args, args.kwonlyargs)


def walk_until(node, stop):
    if isinstance(node, stop):
        return
    yield node
    if isinstance(node, list):
        for e in node:
            yield from walk_until(e, stop)
        return
    for child in ast.iter_child_nodes(node):
        yield from walk_until(child, stop)


def walk_function_nodes(node):
    if isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef, ast.Lambda)):
        for argument in arguments(node):
            if argument.annotation:
                yield from walk_function_nodes(argument.annotation)
        for default in [*node.args.kw_defaults, *node.args.defaults]:
            if default is not None:
                yield from walk_function_nodes(default)

        if isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef)):
            for decorator in node.decorator_list:
                yield from walk_function_nodes(decorator)

            if node.returns is not None:
                yield from walk_function_nodes(node.returns)

        return
    yield node
    if isinstance(node, list):
        for e in node:
            yield from walk_function_nodes(e)
        return
    for child in ast.iter_child_nodes(node):
        yield from walk_function_nodes(child)


def use():
    """
    this function is mocked in test_valid_source to ignore some decisions
    which are usually made by the algo.
    The goal is to try to generate some valid source code which would otherwise not be generated.
    """
    return True


def equal_ast(lhs, rhs, dump_info=False, t="root"):
    if type(lhs) != type(rhs):
        if dump_info:
            print(t, lhs, "!=", rhs)
        return False

    elif isinstance(lhs, list):
        if len(lhs) != len(rhs):
            if dump_info:
                print(t, lhs, "!=", rhs)
            return False

        return all(
            equal_ast(l, r, t + f"[{i}]") for i, (l, r) in enumerate(zip(lhs, rhs))
        )

    elif isinstance(lhs, ast.AST):
        return all(
            equal_ast(getattr(lhs, field), getattr(rhs, field), t + f".{field}")
            for field in lhs._fields
            if field not in ("ctx",)
        )
    else:
        if dump_info and lhs != rhs:
            print(t, lhs, "!=", rhs)
        return lhs == rhs


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
                        last = field_type[-1]
                        if last in "*?":
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
            assert False, "no doc for " + name

    return type_infos[name]


if sys.version_info < (3, 9):
    from .static_type_info import type_infos  # type: ignore


import random


def only_firstone(l, condition):
    found = False
    for i, e in reversed(list(enumerate(l))):
        if condition(e):
            if found:
                del l[i]
            found = True


def unique_by(l, key):
    return list({key(e): e for e in l}.values())


def propability(parents, child_name):
    parent_types = [p[0] for p in parents]

    def inside(types, not_types=()):
        if not isinstance(types, tuple):
            types = (types,)

        for parent, arg in reversed(parents):
            qual_parent = f"{parent}.{arg}"
            if any(qual_parent == t if "." in t else parent == t for t in types):
                return True
            if any(qual_parent == t if "." in t else parent == t for t in not_types):
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
        return 0

    # f-string
    if parents[-1] == ("JoinedStr", "values") and child_name not in (
        "Constant",
        "FormattedValue",
    ):
        return 0

    if 0:
        if (
            not py312plus
            and parents[-1] == ("FormattedValue", "value")
            and child_name != "Constant"
        ):
            # TODO: WHY?
            return 0

    if parents[-1] == ("FormattedValue", "format_spec") and child_name != "JoinedStr":
        return 0

    if (
        child_name == "JoinedStr"
        and parents.count(("FormattedValue", "format_spec")) > f_string_format_limit
    ):
        return 0

    if (
        child_name == "JoinedStr"
        and parents.count(("FormattedValue", "value")) > f_string_expr_limit
    ):
        return 0

    if child_name == "FormattedValue" and parents[-1][0] != "JoinedStr":
        # TODO: doc says this should be valid, maybe a bug in the python doc
        # see https://github.com/python/cpython/issues/111257
        return 0

    if inside(
        ("Delete.targets"), ("Subscript.value", "Subscript.slice", "Attribute.value")
    ) and child_name not in (
        "Name",
        "Attribute",
        "Subscript",
        "List",
        "Tuple",
    ):
        return 0

    # function statements
    if child_name in (
        "Return",
        "Yield",
        "YieldFrom",
    ) and not inside(
        ("FunctionDef.body", "AsyncFunctionDef.body", "Lambda.body"), ("ClassDef.body",)
    ):
        return 0
    # function statements
    if child_name in ("Nonlocal",) and not inside(
        ("FunctionDef.body", "AsyncFunctionDef.body", "Lambda.body", "ClassDef.body")
    ):
        return 0

    if (
        not py38plus
        and child_name == "Continue"
        and inside(
            ("Try.finalbody", "TryStar.finalbody"),
            ("FunctionDef.body", "AsyncFunctionDef.body"),
        )
    ):
        return 0

    if parents[-1] == ("MatchMapping", "keys") and child_name != "Constant":
        # TODO: find all allowed key types
        return 0

    if child_name == "MatchStar" and parent_types[-1] != "MatchSequence":
        return 0

    if child_name == "Starred" and parents[-1] not in (
        ("Tuple", "elts"),
        ("Call", "args"),
        ("List", "elts"),
        ("Set", "elts"),
    ):
        return 0

    assign_target = ("Subscript", "Attribute", "Name", "Starred", "List", "Tuple")

    assign_context = [p for p in parents if p[0] not in ("Tuple", "List", "Starred")]

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
            return 0

    if parents[-1] in [("AugAssign", "target"), ("AnnAssign", "target")]:
        if child_name in ("Starred", "List", "Tuple"):
            return 0

    if inside(("AnnAssign.target",)) and child_name == "Starred":
        # TODO this might be a cpython bug
        return 0

    if parents[-1] in [("AnnAssign", "target")]:
        if child_name not in ("Name", "Attribute", "Subscript"):
            return 0

    if parents[-1] in [("NamedExpr", "target")] and child_name != "Name":
        return 0

    in_async_code = inside(
        "AsyncFunctionDef.body", ("FunctionDef.body", "Lambda.body", "ClassDef.body")
    )

    if child_name in ("AsyncFor", "Await", "AsyncWith") and not in_async_code:
        return 0

    if child_name in ("YieldFrom",) and in_async_code:
        return 0

    in_loop = inside(
        ("For.body", "While.body", "AsyncFor.body"),
        ("FunctionDef.body", "Lambda.body", "AsyncFunctionDef.body", "ClassDef.body"),
    )

    if child_name in ("Break", "Continue") and not in_loop:
        return 0

    if inside("TryStar.handlers") and child_name in ("Break", "Continue", "Return"):
        # SyntaxError: 'break', 'continue' and 'return' cannot appear in an except* block
        return 0

    if inside(("MatchValue",)) and child_name not in (
        "Attribute",
        "Name",
        "Constant",
        "UnaryOp",
        "USub",
    ):
        return 0

    if (
        inside(("MatchValue",))
        and inside(("UnaryOp",))
        and child_name in ("Name", "UnaryOp", "Attribute")
    ):
        return 0

    if parents[-1] == ("MatchValue", "value") and child_name == "Name":
        return 0

    if inside("MatchClass.cls"):
        if child_name not in ("Name", "Attribute"):
            return 0

    if parents[-1] == ("comprehension", "iter") and child_name == "NamedExpr":
        return 0

    if inside(
        ("GeneratorExp", "ListComp", "SetComp", "DictComp", "DictComp")
    ) and child_name in ("Yield", "YieldFrom"):
        # SyntaxError: 'yield' inside list comprehension
        return 0

    if (
        inside(("GeneratorExp", "ListComp", "SetComp", "DictComp", "DictComp"))
        # TODO restrict to comprehension inside ClassDef
        and inside(
            "ClassDef.body",
            ("FunctionDef.body", "AsyncFunctionDef.body", "Lambda.body"),
        )
        and child_name == "NamedExpr"
    ):
        # SyntaxError: assignment expression within a comprehension cannot be used in a class body
        return 0

    if not py39plus and any(p[1] == "decorator_list" for p in parents):
        # restricted decorators
        # see https://peps.python.org/pep-0614/

        deco_parents = list(
            itertools.takewhile(lambda a: a[1] != "decorator_list", reversed(parents))
        )[::-1]

        def valid_deco_parents(parents):
            # Call?,Attribute*
            parents = list(parents)
            if parents and parents[0] == ("Call", "func"):
                parents.pop()
            return all(p == ("Attribute", "value") for p in parents)

        if valid_deco_parents(deco_parents) and child_name != "Name":
            return 0

    # type alias
    if py312plus:
        if parents[-1] == ("TypeAlias", "name") and child_name != "Name":
            return 0

        if child_name in (
            "NamedExpr",
            "Yield",
            "YieldFrom",
            "Await",
            "ListComp",
            "DictComp",
            "SetComp",
            "GeneratorExp",
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
            return 0

        if child_name == "Await" and inside("AnnAssign.annotation"):
            return 0

    if child_name == "Expr":
        return 30

    if child_name == "NonLocal" and parents[-1] == ("Module", "body"):
        return 0

    return 1


def fix(node, parents):
    if isinstance(node, ast.ImportFrom):
        if use() and not py310plus and node.level is None:
            node.level = 0

        if use() and node.module == None and (node.level == None or node.level == 0):
            node.level = 1

    if isinstance(node, ast.ExceptHandler):
        if use() and node.type is None:
            node.name = None

    if (
        sys.version_info < (3, 11)
        and isinstance(node, ast.Tuple)
        and parents[-1] == ("Subscript", "slice")
    ):
        # a[(a:b,*c)] <- not valid
        # TODO check this
        found = False
        new_elts = []
        # allow only the first Slice or Starred
        for e in node.elts:
            if isinstance(e, (ast.Starred, ast.Slice)):
                if not found:
                    new_elts.append(e)
                    found = True
            else:
                new_elts.append(e)
        node.elts = new_elts

    if isinstance(node, ast.Constant):
        # TODO: what is Constant.kind
        # Constant.kind can be u for unicode strings
        allowed_kind: list[str | None] = [None]
        if isinstance(node.value, str):
            allowed_kind.append("u")
        elif node.kind not in allowed_kind:
            node.kind = allowed_kind[hash(node.kind) % len(allowed_kind)]

        if (
            use()
            and parents
            and parents[-1] == ("JoinedStr", "values")
            and not isinstance(node.value, str)
        ):
            # TODO: better format string generation
            node.value = str(node.value)

    if isinstance(node, ast.FormattedValue):
        valid_conversion = (-1, 115, 114, 97)
        if use() and not py310plus and node.conversion is None:
            node.conversion = 5
        if use() and node.conversion not in valid_conversion:
            node.conversion = valid_conversion[node.conversion % 4]

    assign_context = [p for p in parents if p[0] not in ("Tuple", "List", "Starred")]

    if hasattr(node, "ctx"):
        if use() and parents and parents[-1] == ("Delete", "targets"):
            node.ctx = ast.Del()
        elif (
            use()
            and assign_context
            and assign_context[-1]
            in (
                ("Assign", "targets"),
                ("AnnAssign", "target"),
                ("For", "target"),
                ("AsyncFor", "target"),
                ("withitem", "optional_vars"),
                ("comprehension", "target"),
            )
        ):
            node.ctx = ast.Store()
        elif use():
            node.ctx = ast.Load()

    if (
        use()
        and isinstance(node, (ast.List, ast.Tuple))
        and isinstance(node.ctx, ast.Store)
    ):
        only_firstone(node.elts, lambda e: isinstance(e, ast.Starred))

    if use() and isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef, ast.Lambda)):
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

    if use() and isinstance(node, ast.AsyncFunctionDef):
        if any(
            isinstance(n, (ast.Yield, ast.YieldFrom))
            for n in walk_function_nodes(node.body)
        ):
            for n in walk_function_nodes(node.body):
                if isinstance(n, ast.Return):
                    n.value = None

    if use() and isinstance(node, (ast.ClassDef, ast.Call)):
        # unique argument names
        seen = set()
        for i, kw in reversed(list(enumerate(node.keywords))):
            if kw.arg:
                if kw.arg in seen:
                    del node.keywords[i]
                seen.add(kw.arg)

    if use() and isinstance(node, (ast.Try)):
        node.handlers[:-1] = [
            handler for handler in node.handlers[:-1] if handler.type is not None
        ]
        if use() and not node.handlers:
            node.orelse = []

    if use() and sys.version_info >= (3, 11) and isinstance(node, ast.TryStar):
        node.handlers = [
            handler for handler in node.handlers if handler.type is not None
        ]
        if use() and not node.handlers:
            node.orelse = []

    if use() and isinstance(
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

        class Transformer(ast.NodeTransformer):
            def visit_NamedExpr(self, node: ast.NamedExpr):
                if use() and node.target.id in names:
                    return self.visit(node.value)
                return self.generic_visit(node)

        node = Transformer().visit(node)

    # pattern matching
    if sys.version_info >= (3, 10):

        def match_wildcard(node):
            if isinstance(node, ast.MatchAs):
                return (
                    node.pattern is None
                    or match_wildcard(node.pattern)
                    or node.name is None
                )
            if isinstance(node, ast.MatchOr):
                return any(match_wildcard(p) for p in node.patterns)

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

        # @lambda f:lambda pattern:set(f(pattern))
        def names(node):
            if isinstance(node, ast.MatchAs) and node.name:
                yield node.name
            elif isinstance(node, ast.MatchStar) and node.name:
                yield node.name
            elif isinstance(node, ast.MatchMapping) and node.rest:
                yield node.rest
            elif isinstance(node, ast.MatchOr):
                yield from set.intersection(
                    *[set(names(pattern)) for pattern in node.patterns]
                )
            else:
                for child in ast.iter_child_nodes(node):
                    yield from names(child)

        class RemoveName(ast.NodeVisitor):
            def __init__(self, condition):
                self.condition = condition

            def visit_MatchAs(self, node):
                if self.condition(node.name):
                    node.name = None

            def visit_MatchMapping(self, node):
                if self.condition(node.rest):
                    node.rest = None

        class FixPatternNames(ast.NodeTransformer):
            def __init__(self, used=None, allowed=None):
                # variables which are already used
                self.used = set() if used is None else used
                # variables which are allowed in a MatchOr
                self.allowed = allowed

            def is_allowed(self, name):
                return (
                    name is None
                    or name not in self.used
                    and (name in self.allowed if self.allowed is not None else True)
                )

            def visit_MatchAs(self, node):
                if not self.is_allowed(node.name):
                    return ast.Constant(value=None)
                elif node.name is not None:
                    self.used.add(node.name)
                return self.generic_visit(node)

            def visit_MatchStar(self, node):
                if not self.is_allowed(node.name):
                    return ast.Constant(value=None)
                elif node.name is not None:
                    self.used.add(node.name)
                return self.generic_visit(node)

            def visit_MatchMapping(self, node):
                if not self.is_allowed(node.rest):
                    return ast.Constant(value=None)
                elif node.rest is not None:
                    self.used.add(node.rest)
                return self.generic_visit(node)

            def visit_MatchOr(self, node: ast.MatchOr):
                allowed = set.intersection(
                    *[set(names(pattern)) for pattern in node.patterns]
                )
                allowed -= self.used

                node.patterns = [
                    FixPatternNames(set(self.used), allowed).visit(child)
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
                seen |= {*names(pattern)}

        if isinstance(node, ast.MatchAs):
            if node.name is None:
                node.pattern = None

        if isinstance(node, ast.MatchOr):
            var_names = set.intersection(
                *[set(names(pattern)) for pattern in node.patterns]
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
                seen |= {*names(pattern)}

        if isinstance(node, ast.MatchClass):
            node.kwd_attrs = list(set(node.kwd_attrs))
            del node.kwd_patterns[len(node.kwd_attrs) :]

            seen = set()
            for pattern in [*node.patterns, *node.kwd_patterns]:
                RemoveName(lambda name: name in seen).visit(pattern)
                seen |= {*names(pattern)}

    # async nodes

    in_async_code = False
    for parent, attr in reversed(parents):
        if parent == "AsyncFunctionDef" and attr == "body":
            in_async_code = True
            break
        if parent in ("FunctionDef", "Lambda", "ClassDef"):
            break

        if not py311plus and parent in (
            "ListComp",
            "DictComp",
            "SetComp",
            "GeneratorExp",
        ):
            break

    if isinstance(node, (ast.ListComp, ast.SetComp, ast.DictComp)):
        if use() and not in_async_code:
            for comp in node.generators:
                comp.is_async = 0

    in_excepthandler = False
    for parent, _ in reversed(parents):
        if parent == "ExceptHandler":
            in_excepthandler = True
            break
        if parent in ("FunctionDef", "Lambda", "AsyncFunctionDef"):
            break

    if isinstance(node, ast.Raise):
        if use() and not node.exc:
            node.cause = None

    if use() and isinstance(node, ast.Lambda):
        # no annotation for lambda arguments
        for args in all_args(node.args):
            for arg in args:
                arg.annotation = None

        if use() and node.args.vararg:
            node.args.vararg.annotation = None

        if use() and node.args.kwarg:
            node.args.kwarg.annotation = None

    if sys.version_info >= (3, 12):
        if use() and isinstance(node, ast.Global):
            node.names = unique_by(node.names, lambda e: e)

        # type scopes
        if use() and hasattr(node, "type_params"):
            node.type_params = unique_by(node.type_params, lambda p: p.name)

        def cleanup_annotation(annotation):
            class Transformer(ast.NodeTransformer):
                def visit_NamedExpr(self, node: ast.NamedExpr):
                    if not use():
                        return self.generic_visit(node)
                    return self.visit(node.value)

                def visit_Yield(self, node: ast.Yield) -> Any:
                    if not use():
                        return self.generic_visit(node)
                    if node.value is None:
                        return ast.Constant(value=None)
                    return self.visit(node.value)

                def visit_YieldFrom(self, node: ast.YieldFrom) -> Any:
                    if not use():
                        return self.generic_visit(node)
                    return self.visit(node.value)

                def visit_Lambda(self, node: ast.Lambda) -> Any:
                    if not use():
                        return self.generic_visit(node)
                    return self.visit(node.body)

            return Transformer().visit(annotation)

        if (
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.type_params
        ):
            for arg in [
                *node.args.posonlyargs,
                *node.args.args,
                *node.args.kwonlyargs,
                node.args.vararg,
                node.args.kwarg,
            ]:
                if use() and arg is not None and arg.annotation:
                    arg.annotation = cleanup_annotation(arg.annotation)

            if use() and node.returns is not None:
                node.returns = cleanup_annotation(node.returns)

        if isinstance(node, ast.ClassDef) and node.type_params:
            node.bases = [cleanup_annotation(b) for b in node.bases]
            for kw in node.keywords:
                if use():
                    kw.value = cleanup_annotation(kw.value)

            for n in ast.walk(node):
                if use() and isinstance(n, ast.TypeAlias):
                    n.value = cleanup_annotation(n.value)

        if isinstance(node, ast.ClassDef):
            for n in ast.walk(node):
                if use() and isinstance(n, ast.TypeVar) and n.bound is not None:
                    n.bound = cleanup_annotation(n.bound)

        if use() and isinstance(node, ast.AnnAssign):
            node.annotation = cleanup_annotation(node.annotation)

    return node


def fix_result(node):
    return fix_nonlocal(node)


def is_valid_ast(tree) -> bool:
    def is_valid(node: ast.AST, parents):
        node_type = node.__class__.__name__
        if (
            isinstance(node, (ast.AST))
            and parents
            and propability(
                parents,
                node_type,
            )
            == 0
        ):
            print("invalid node with:")
            print("parents:", parents)
            print("node:", node)
            if 0:
                breakpoint()
                propability(
                    parents,
                    node.__class__.__name__,
                )

            return False

        if node_type in same_length:
            attrs = same_length[node_type]
            if len({len(v) for k, v in ast.iter_fields(node) if k in attrs}) != 1:
                return False

        if isinstance(node, (ast.AST)):
            for field in node._fields:
                value = getattr(node, field)
                if isinstance(value, list):
                    if not all(
                        is_valid(e, parents + [(node.__class__.__name__, field)])
                        for e in value
                    ):
                        return False
                else:
                    if not is_valid(
                        value, parents + [(node.__class__.__name__, field)]
                    ):
                        return False
        return True

    if not is_valid(tree, []):
        return False

    for node in ast.walk(tree):
        type_name = node.__class__.__name__
        info = get_info(type_name)

        for attr_name, value in ast.iter_fields(node):
            if isinstance(value, list) and len(value) < min_attr_length(
                type_name, attr_name
            ):
                print("invalid arg length", type_name, attr_name)
                return False

            if isinstance(value, list) != (info.fields[attr_name][1] == "*"):
                print("no list", value)
                return False
            if value is None:
                if (
                    info.fields[attr_name][1] != "?"
                    and info.fields[attr_name][0] != "constant"
                ):
                    print("none not allowed", type_name, attr_name)
                    return False

    tree_copy = deepcopy(tree)

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
                        fix_tree(v, parents + [(node.__class__.__name__, field)])
                        if isinstance(v, ast.AST)
                        else v
                        for v in value
                    ],
                )

        return fix(node, parents)

    tree_copy = fix_tree(tree_copy, [])
    tree_copy = fix_result(tree_copy)

    result = equal_ast(tree_copy, tree)

    if 1:
        if sys.version_info >= (3, 9) and not result:
            dump_copy = ast_dump(tree_copy).splitlines()
            dump = ast_dump(tree).splitlines()
            import difflib

            print("\n".join(difflib.unified_diff(dump, dump_copy, "original", "fixed")))

    return result


def arguments(
    node: ast.FunctionDef | ast.AsyncFunctionDef | ast.Lambda,
) -> list[ast.arg]:
    args = node.args
    l = [
        *args.args,
        args.vararg,
        *args.kwonlyargs,
        args.kwarg,
    ]

    l += args.posonlyargs

    return [arg for arg in l if arg is not None]


def fix_nonlocal(node):
    class NonLocalFixer(ast.NodeTransformer):
        """
        removes invalid Nonlocals from the class/function
        """

        def __init__(self, locals, nonlocals, globals, type_params):
            self.locals = set(locals)
            self.used_names = set(locals)
            self.type_params = set(type_params)

            # nonlocals from the parent scope
            self.nonlocals = set(nonlocals)
            self.used_nonlocals = set()

            # globals from the global scope
            self.globals = set(globals)
            self.used_globals = set()

        def name_assigned(self, name):
            self.locals.add(name)
            self.used_names.add(name)

        def visit_Name(self, node: ast.Name) -> Any:
            if isinstance(node.ctx, (ast.Store, ast.Del)):
                self.name_assigned(node.id)
            else:
                self.used_names.add(node.id)
            return node

        if sys.version_info >= (3, 10):

            def visit_MatchAs(self, node: ast.MatchAs) -> Any:
                if node.pattern:
                    self.visit(node.pattern)
                self.name_assigned(node.name)
                return node

        def visit_GeneratorExp(self, node: ast.GeneratorExp) -> Any:
            self.visit(node.generators[0].iter)
            return node

        def visit_ListComp(self, node: ast.ListComp) -> Any:
            self.visit(node.generators[0].iter)
            return node

        def visit_DictComp(self, node: ast.DictComp) -> Any:
            self.visit(node.generators[0].iter)
            return node

        def visit_SetComp(self, node: ast.SetComp) -> Any:
            self.visit(node.generators[0].iter)
            return node

        def visit_Nonlocal(self, node: ast.Nonlocal) -> Any:
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
                and name not in self.used_globals
                or name in ("__class__",)
            ]
            self.used_nonlocals |= set(node.names)

            if not node.names:
                return ast.Pass()

            return node

        def visit_Global(self, node: ast.Global) -> Any:
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

        def visit_AnnAssign(self, node: ast.AnnAssign) -> Any:
            if isinstance(node.target, ast.Name) and (
                node.target.id in self.used_globals
                or node.target.id in self.used_nonlocals
            ):
                if node.value:
                    return self.generic_visit(
                        ast.Assign(targets=[node.target], value=node.value)
                    )
                else:
                    return ast.Pass()
            return self.generic_visit(node)

        def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
            self.name_assigned(node.name)

            all_nodes = [
                *node.args.defaults,
                *node.args.kw_defaults,
                *node.decorator_list,
                node.returns,
            ]

            if sys.version_info < (3, 12):
                all_nodes += [arg.annotation for arg in arguments(node)]

            for default in all_nodes:
                if default is not None:
                    self.visit(default)
            return node

        def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> Any:
            self.name_assigned(node.name)

            all_nodes = [
                *node.args.defaults,
                *node.args.kw_defaults,
                *node.decorator_list,
                node.returns,
            ]

            if sys.version_info < (3, 12):
                all_nodes += [arg.annotation for arg in arguments(node)]

            for default in all_nodes:
                if default is not None:
                    self.visit(default)
            return node

        def visit_ClassDef(self, node: ast.ClassDef) -> Any:
            for expr in [
                *[k.value for k in node.keywords],
                *node.bases,
                *node.decorator_list,
            ]:
                if expr is not None:
                    self.visit(expr)

            self.name_assigned(node.name)

            return node

        def visit_ExceptHandler(self, handler):
            if handler.name:
                self.name_assigned(handler.name)
            return self.generic_visit(handler)

        def visit_Lambda(self, node: ast.Lambda) -> Any:
            for default in [*node.args.defaults, *node.args.kw_defaults]:
                if default is not None:
                    self.visit(default)
            return node

        if sys.version_info < (3, 13):

            def visit_Try(self, node: ast.Try) -> Any:
                # work around for https://github.com/python/cpython/issues/111123
                args = {}
                for k in ("body", "orelse", "handlers", "finalbody"):
                    args[k] = [self.visit(x) for x in getattr(node, k)]

                return ast.Try(**args)

            if sys.version_info >= (3, 11):

                def visit_TryStar(self, node: ast.TryStar) -> Any:
                    # work around for https://github.com/python/cpython/issues/111123
                    args = {}
                    for k in ("body", "orelse", "handlers", "finalbody"):
                        args[k] = [self.visit(x) for x in getattr(node, k)]

                    return ast.TryStar(**args)

    class FunctionTransformer(ast.NodeTransformer):
        """
        - transformes a class/function
        """

        def __init__(self, nonlocals, globals, type_params):
            self.nonlocals = set(nonlocals)
            self.globals = set(globals)
            self.type_params = type_params

        def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
            return self.handle_function(node)

        def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> Any:
            return self.handle_function(node)

        def visit_Lambda(self, node: ast.Lambda) -> Any:
            # there are no globals/nonlocals/functiondefs in lambdas
            return node

        def visit_ClassDef(self, node: ast.ClassDef) -> Any:
            type_params = set(self.type_params)
            if sys.version_info >= (3, 12):
                type_params |= {typ.name for typ in node.type_params}  # type: ignore

            fixer = NonLocalFixer([], self.nonlocals, self.globals, type_params)
            node.body = [fixer.visit(stmt) for stmt in node.body]

            ft = FunctionTransformer(self.nonlocals, self.globals, type_params)
            node.body = [ft.visit(stmt) for stmt in node.body]

            return node

        def handle_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> Any:
            names = {arg.arg for arg in arguments(node)}

            type_params = set(self.type_params)
            if sys.version_info >= (3, 12):
                type_params |= {typ.name for typ in node.type_params}  # type: ignore

            fixer = NonLocalFixer(names, self.nonlocals, self.globals, type_params)
            node.body = [fixer.visit(stmt) for stmt in node.body]

            ft = FunctionTransformer(
                fixer.locals | self.nonlocals, self.globals, type_params
            )
            node.body = [ft.visit(stmt) for stmt in node.body]

            return node

    fixer = NonLocalFixer([], [], [], [])
    node = fixer.visit(node)

    node = FunctionTransformer([], [], []).visit(node)
    return node


def min_attr_length(node_type, attr_name):
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
    if sys.version_info < (3, 9) and node_type == "Set" and attr_name == "elts":
        return 1
    if node_type == "Compare" and attr_name in ("ops", "comparators"):
        return 1
    if attr_name == "generators":
        return 1

    return 0


same_length = {
    "MatchClass": ["kwd_attrs", "kwd_patterns"],
    "MatchMapping": ["patterns", "keys"],
    "arguments": ["kw_defaults", "kwonlyargs"],
}


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
                    return self.generate_impl(t, parents, depth) if self.cnd() else None
                else:
                    assert False

            attributes = {
                n: child_node(n, t, q, [*parents, (name, n)])
                for n, (t, q) in info.fields.items()
            }

            result = info.ast_type(**attributes)
            result = fix(result, parents)
            return result

        if isinstance(info, UnionNodeType):
            options_list = [
                (option, propability(parents, option)) for option in info.options
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


# next algo

# design targets:
# * enumerate "all" possible ast-node combinations
# * check if propability 0 would produce incorrect code
#   * the algo should be able to generate every possible syntax combination for every python version.
# * hypothesis integration
# * do not use compile() in the implementation
# * generation should be customizable (custom propabilities and random values)

# features:
# * node-context: function-scope async-scope type-scope class-scope ...
# * names: nonlocal global

from dataclasses import dataclass


@dataclass
class ParentRef:
    node: PartialNode
    attr_name: str
    index: int
    _context: dict

    def __getattr__(self, name):
        if name.startswith("ctx_"):
            return getattr(node, name)
        raise AttributeError


# (d:=[n] | q_parent("Delete.targets")) and len(d.targets)==1


@dataclass
class PartialValue:
    value: int | str | bool


@dataclass
class PartialNode:
    _node_type_name: str
    parent_ref: ParentRef | None
    _defined_attrs: dict
    _context: dict

    def inside(self, spec) -> PartialNode | None:
        ...

    @property
    def parent(self):
        return self.parent_ref.node

    def __getattr__(self, name):
        if name.startswith("ctx_"):
            return getattr(node, name)

        if name not in self._defined_attrs:
            raise RuntimeError(f"{self._node_type_name}.{name} is not defined jet")

        return self._defined_attrs[name]


def gen(node: PartialNode):
    # parents [(node,attr_name)]
    pass
