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

py38plus = (3, 8) <= sys.version_info
py39plus = (3, 9) <= sys.version_info
py310plus = (3, 10) <= sys.version_info
py311plus = (3, 11) <= sys.version_info
py312plus = (3, 12) <= sys.version_info

type_infos: dict[str, NodeType | BuiltinNodeType | UnionNodeType] = {}

before_compile_hook = lambda code: None


def all_args(args):
    if py38plus:
        return (args.posonlyargs, args.args, args.kwonlyargs)
    else:
        return (args.args, args.kwonlyargs)


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
            assert False, "no doc"

    return type_infos[name]


if sys.version_info < (3, 8):
    from .static_type_info37 import type_infos  # type: ignore
elif sys.version_info < (3, 9):
    from .static_type_info import type_infos  # type: ignore


get_info("Delete").fields = {"targets": ("_deleteTargets", "*")}
type_infos["_deleteTargets"] = UnionNodeType(options=["Name", "Attribute", "Subscript"])


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

    if child_name == "Slice":
        if parents[-1] != ("Subscript", "slice") or parents[-2:] != [
            ("Subscript", "slice"),
            ("Tuple", "elts"),
        ]:
            return 0

    # f-string
    if parents[-1] == ("JoinedStr", "values") and child_name not in (
        "Constant",
        "FormattedValue",
    ):
        return 0

    if (
        not py312plus
        and parents[-1] == ("FormattedValue", "value")
        and child_name != "Constant"
    ):
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
        return 0

    # function statements
    if child_name in (
        "Nonlocal",
        "Return",
        "Yield",
        "YieldFrom",
        "Continue",
    ) and not inside(("FunctionDef.body", "AsyncFunctionDef.body"), ("ClassDef.body",)):
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

    if [p for p in parents if p[0] not in ("Tuple", "List", "Starred")][-1] in [
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

    if parents[-1] in [("AnnAssign", "target")]:
        if child_name != "Name":
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
        ("For.body", "While.body"),
        ("FunctionDef.body", "Lambda.body", "AsyncFunctionDef.body", "ClassDef.body"),
    )

    if child_name in ("Break", "Continue") and not in_loop:
        return 0

    if inside("TryStar.handlers") and child_name in ("Break", "Continue", "Return"):
        # SyntaxError: 'break', 'continue' and 'return' cannot appear in an except* block
        return 0

    if inside(("MatchValue",)) and child_name not in ("Attribute", "Name"):
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

    return 1


def fix(node, parents):
    if isinstance(node, ast.ImportFrom):
        if not py310plus and node.level is None:
            node.level = 0

        if node.module == None and (node.level == None or node.level == 0):
            node.level = 1

    if isinstance(node, ast.ExceptHandler):
        if node.type is None:
            node.name = None

    if isinstance(node, ast.Constant):
        # TODO: what is Constant.kind
        node.kind = None
        if parents[-1][0] == "JoinedStr":
            # TODO: better format string generation
            node.value = "text"

    if isinstance(node, ast.FormattedValue):
        if not py310plus and node.conversion is None:
            node.conversion = 5
        node.conversion = [-1, 115, 114, 97][node.conversion % 4]

    if hasattr(node, "ctx"):
        if parents[-1] == ("Delete", "targets"):
            node.ctx = ast.Del()
        elif [p for p in parents if p[0] not in ("Tuple", "List", "Starred")][-1] in (
            ("Assign", "targets"),
            ("For", "target"),
            ("AsyncFor", "target"),
            ("withitem", "optional_vars"),
            ("comprehension", "target"),
        ):
            node.ctx = ast.Store()
        else:
            node.ctx = ast.Load()

    if isinstance(node, (ast.List, ast.Tuple)) and isinstance(node.ctx, ast.Store):
        only_firstone(node.elts, lambda e: isinstance(e, ast.Starred))

    if isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef, ast.Lambda)):
        # unique argument names
        seen = set()
        for args in all_args(node.args):
            for i, arg in reversed(list(enumerate(args))):
                if arg.arg in seen:
                    del args[i]
                seen.add(arg.arg)

        for arg_name in ("kwarg", "vararg"):
            arg = getattr(node.args, arg_name)
            if arg:
                if arg.arg in seen:
                    setattr(node.args, arg_name, None)
                seen.add(arg.arg)

    if isinstance(node, ast.AsyncFunctionDef):
        if any(
            isinstance(n, (ast.Yield, ast.YieldFrom))
            for b in node.body
            for n in ast.walk(b)
        ):
            for n in ast.walk(node):
                if isinstance(n, ast.Return):
                    n.value = None

    if isinstance(node, (ast.ClassDef, ast.Call)):
        # unique argument names
        seen = set()
        for i, kw in reversed(list(enumerate(node.keywords))):
            if kw.arg:
                if kw.arg in seen:
                    del node.keywords[i]
                seen.add(kw.arg)

    if isinstance(node, (ast.Try)):
        node.handlers[:-1] = [
            handler for handler in node.handlers[:-1] if handler.type is not None
        ]
        if not node.handlers:
            node.orelse = []

    if sys.version_info >= (3, 11) and isinstance(node, ast.TryStar):
        node.handlers = [
            handler for handler in node.handlers if handler.type is not None
        ]
        if not node.handlers:
            node.orelse = []

    if sys.version_info >= (3, 8) and isinstance(
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
                if node.target.id in names:
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
                if match_wildcard(p):
                    if not found:
                        new_last = node.cases[i]
                        found = True
                    del node.cases[i]
            if new_last:
                node.cases.append(new_last)

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
                if (
                    isinstance(case.pattern, ast.MatchAs)
                    and case.pattern.name is None
                    or isinstance(case.pattern, ast.MatchOr)
                    and isinstance(case.pattern.patterns[-1], ast.MatchAs)
                    and case.pattern.patterns[-1].name is None
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

    if hasattr(node, "generators"):
        if not in_async_code:
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
        if not in_excepthandler or not node.exc:
            node.cause = None

        if not in_excepthandler and not node.exc:
            return ast.Pass()

    if isinstance(node, ast.Lambda):
        # no annotation for lambda arguments
        for args in all_args(node.args):
            for arg in args:
                arg.annotation = None

        if node.args.vararg:
            node.args.vararg.annotation = None

        if node.args.kwarg:
            node.args.kwarg.annotation = None

    if sys.version_info >= (3, 12):
        if isinstance(node, ast.Global):
            node.names = list(set(node.names))

        # type scopes
        if hasattr(node, "type_params"):
            node.type_params = unique_by(node.type_params, lambda p: p.name)

        def cleanup_annotation(annotation):
            class Transformer(ast.NodeTransformer):
                def visit_NamedExpr(self, node: ast.NamedExpr):
                    return self.visit(node.value)

                def visit_Yield(self, node: ast.Yield) -> Any:
                    if node.value is None:
                        return ast.Constant(value=None)
                    return self.visit(node.value)

                def visit_YieldFrom(self, node: ast.YieldFrom) -> Any:
                    return self.visit(node.value)

                def visit_Lambda(self, node: ast.Lambda) -> Any:
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
                if arg is not None and arg.annotation:
                    arg.annotation = cleanup_annotation(arg.annotation)

            if node.returns is not None:
                node.returns = cleanup_annotation(node.returns)

        if isinstance(node, ast.ClassDef) and node.type_params:
            node.bases = [cleanup_annotation(b) for b in node.bases]
            for kw in node.keywords:
                kw.value = cleanup_annotation(kw.value)

            for n in ast.walk(node):
                if isinstance(n, ast.TypeAlias):
                    n.value = cleanup_annotation(n.value)

        if isinstance(node, ast.ClassDef):
            for n in ast.walk(node):
                if isinstance(n, ast.TypeVar) and n.bound is not None:
                    n.bound = cleanup_annotation(n.bound)

        if isinstance(node, ast.AnnAssign):
            node.annotation = cleanup_annotation(node.annotation)

    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Module)):
        while True:
            try:
                if hasattr(node, "args"):
                    tmp_node = deepcopy(node)

                    tmp_node.args.posonlyargs = []
                    tmp_node.args.args = []
                    tmp_node.args.vararg = None
                    tmp_node.args.kwonlyargs = []
                    tmp_node.args.kwarg = None
                    if 0:
                        tmp_node.args.defaults = []
                        tmp_node.args.kw_defaults = []

                    tmp_node.decorator_list = []
                    tmp_node.returns = None
                else:
                    tmp_node = node

                code = unparse(ast.fix_missing_locations(tmp_node))

                before_compile_hook(code)

                # code="async def foo():\n"+textwrap.indent(code,"    ")

                compile(code, "<string>", "exec", dont_inherit=True)
                break
            except ValueError:
                break
            except SyntaxError as e:
                # invalid global
                m = re.match("name '(.*)' is used prior to global declaration", str(e))

                if not m:
                    m = re.match(
                        "name '(.*)' is assigned to before global declaration", str(e)
                    )

                if not m:
                    m = re.match("name '(.*)' is parameter and global", str(e))
                if not m:
                    m = re.match("annotated name '(.*)' can't be global", str(e))
                if not m:
                    m = re.match("name '(.*)' is nonlocal and global", str(e))

                if m:
                    name = m.group(1)

                    class Transformer(ast.NodeTransformer):
                        def visit_Global(self, node):
                            node.names = [n for n in node.names if n != name]
                            if not node.names:
                                return ast.Pass()
                            return node

                    node = Transformer().visit(node)
                    continue

                # invalid nonlocal
                m = re.match("name '(.*)' is parameter and nonlocal", str(e))
                if not m:
                    m = re.match(
                        "name '(.*)' is used prior to nonlocal declaration", str(e)
                    )
                if not m:
                    m = re.match("no binding for nonlocal '(.*)' found", str(e))
                if not m:
                    m = re.match(
                        "name '(.*)' is assigned to before nonlocal declaration", str(e)
                    )
                if not m:
                    m = re.match("annotated name '(.*)' can't be nonlocal", str(e))
                if not m:
                    m = re.match(
                        "nonlocal binding not allowed for type parameter '(.*)'", str(e)
                    )

                if m:
                    name = m.group(1)

                    class Transformer(ast.NodeTransformer):
                        def visit_Nonlocal(self, node):
                            if name in node.names:
                                node.names.remove(name)
                            if not node.names:
                                return ast.Pass()
                            return node

                    node = Transformer().visit(node)
                    continue

                raise

    return node


class AstGenerator:
    def __init__(self, seed, node_limit, depth_limit):
        self.rand = random.Random(seed)
        self.nodes = 0
        self.node_limit = node_limit
        self.depth_limit = depth_limit

    def cnd(self):
        return self.rand.choice([True, False])

    def generate(self, name: str, parents=(), depth=0):
        depth += 1
        self.nodes += 1

        if depth > 100:
            exit()

        stop = depth > self.depth_limit or self.nodes > self.node_limit

        info = get_info(name)

        if isinstance(info, NodeType):
            ranges = {}

            def range_for(child, attr_name):
                if name == "Module":
                    return range(20, 30)

                if name == "MatchClass" and attr_name == "kwd_patterns":
                    attr_name = "kwd_attrs"

                if name == "MatchMapping" and attr_name == "patterns":
                    attr_name = "keys"

                if attr_name not in ranges:
                    min = 1 if attr_name == "body" else 0
                    if child == "MatchOr" and attr_name == "patterns":
                        min = 2
                    max = min if stop else min + 1 if depth > 10 else min + 5
                    max = self.rand.randint(min + 1, max + 1)
                    ranges[attr_name] = range(0, max)

                return ranges[attr_name]

            def child_node(n, t, q, parents):
                if q == "":
                    return self.generate(t, parents, depth)
                elif q == "*":
                    return [
                        self.generate(t, parents, depth)
                        for _ in range_for(parents[-1][0], n)
                    ]
                elif q == "?":
                    return self.generate(t, parents, depth) if self.cnd() else None
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
            options = {option: propability(parents, option) for option in info.options}
            if stop:
                for final in ("Name", "MatchValue", "Pass"):
                    if options.get(final, 0) != 0:
                        options = {final: 1}
                        break

            if sum(options.values()) == 0:
                # TODO: better handling of `type?`
                return None

            return self.generate(
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
                    [None, "some const text", "", 1, 0, True, False]
                )

            else:
                assert False, "unknown kind: " + info.kind

        assert False


import warnings


def generate(
    seed: int,
    *,
    node_limit: int = 10000000,
    depth_limit: int = 8,
    root_node: str = "Module",
) -> str:
    generator = AstGenerator(seed, depth_limit=depth_limit, node_limit=node_limit)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", SyntaxWarning)
        tree = generator.generate(root_node)

    ast.fix_missing_locations(tree)
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
