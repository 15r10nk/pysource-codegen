import ast
import inspect
import re
from dataclasses import dataclass, field


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
        doc = inspect.getdoc(getattr(ast, name)) or ""
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

    if parents[-1] == ("FormattedValue", "value") and child_name != "Constant":
        return 0

    if parents[-1] == ("FormattedValue", "format_spec") and child_name != "JoinedStr":
        return 0

    if parents[-1] == ("JoinedStr", "values") and child_name not in (
        "Constant",
        "FormattedValue",
    ):
        return 0

    if child_name == "JoinedStr" and parent_types.count("JoinedStr") >= 2:
        return 0

    if child_name == "FormattedValue" and parents[-1][0] != "JoinedStr":
        # TODO: doc says this should be valid, maybe a bug in the python doc
        return 0

    if child_name in (
        "Nonlocal",
        "Return",
        "Yield",
        "YieldFrom",
        "Continue",
    ) and not inside(("FunctionDef.body", "AsyncFunctionDef.body"), ("ClassDef.body",)):
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

    if [p for p in parents if p[0] not in ("Tuple", "List")][-1] in [
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
        "AsyncFunctionDef.body", ("FunctionDef.body", "Lamda.body", "ClassDef.body")
    )

    if child_name in ("AsyncFor", "Await", "AsyncWith") and not in_async_code:
        return 0

    if child_name in ("YieldFrom",) and in_async_code:
        return 0

    in_loop = inside(
        ("For.body", "While.body"),
        ("FunctionDef.body", "Lamda.body", "AsyncFunctionDef.body", "ClassDef.body"),
    )

    if child_name in ("Break", "Continue") and not in_loop:
        return 0

    if inside(("MatchValue",)) and child_name not in ("Attribute", "Name"):
        return 0

    if parents[-1] == ("MatchValue", "value") and child_name == "Name":
        return 0

    if inside("MatchClass.cls"):
        if child_name not in ("Name", "Attribute", "Subscript"):
            return 0

    return 1


def fix(node, parents):
    if isinstance(node, ast.ImportFrom):
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
        node.conversion = [-1, 115, 114, 97][node.conversion % 4]

    if hasattr(node, "ctx"):
        if parents[-1] == ("Delete", "targets"):
            node.ctx = ast.Del()
        elif parents[-1] in (
            ("Assign", "targets"),
            ("For", "target"),
            ("withitem", "optional_vars"),
        ):
            node.ctx = ast.Store()
        else:
            node.ctx = ast.Load()

    if isinstance(node, (ast.List, ast.Tuple)) and isinstance(node.ctx, ast.Store):
        only_firstone(node.elts, lambda e: isinstance(e, ast.Starred))

    if isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef, ast.Lambda)):
        # unique argument names
        seen = set()
        for args in (node.args.posonlyargs, node.args.args, node.args.kwonlyargs):
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

    if isinstance(node, ast.TryStar):
        node.handlers = [
            handler for handler in node.handlers if handler.type is not None
        ]
        if not node.handlers:
            node.orelse = []

    if isinstance(node, (ast.GeneratorExp, ast.ListComp, ast.DictComp, ast.SetComp)):
        names = [
            n.id
            for c in node.generators
            for n in ast.walk(c.target)
            if isinstance(n, ast.Name)
        ]

        class Transformer(ast.NodeTransformer):
            def visit_NamedExpr(self, node: ast.NamedExpr):
                if node.target.id in names:
                    return node.value
                return node

        node = Transformer().visit(node)

    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Module)):
        while True:
            try:
                code = ast.unparse(ast.fix_missing_locations(node))
                compile(code, "<string>", "exec")
                break
            except ValueError:
                break
            except SyntaxError as e:
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
                            if name in node.names:
                                node.names.remove(name)
                            if not node.names:
                                return ast.Pass()
                            return node

                    node = Transformer().visit(node)
                    continue

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

                break

    if isinstance(node, ast.Match):
        found = False
        new_last = None
        for i, case_ in reversed(list(enumerate(node.cases))):
            p = case_.pattern
            if isinstance(p, ast.MatchAs) and p.pattern is None:
                if not found:
                    new_last = node.cases[i]
                    found = True
                del node.cases[i]
        if new_last:
            node.cases.append(new_last)

    if isinstance(node, ast.MatchClass):
        node.kwd_attrs = list(set(node.kwd_attrs))
        del node.kwd_patterns[len(node.kwd_attrs) :]

    if isinstance(node, ast.MatchMapping):
        node.keys = unique_by(node.keys, ast.literal_eval)
        del node.patterns[len(node.keys) :]

    if isinstance(node, ast.MatchAs):
        if node.name is None:
            node.pattern = None

    in_async_code = False
    for parent, attr in reversed(parents):
        if parent == "AsyncFunctionDef" and attr == "body":
            in_async_code = True
            break
        if parent in ("FunctionDef", "Lamda"):
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
        if parent in ("FunctionDef", "Lamda", "AsyncFunctionDef"):
            break

    if isinstance(node, ast.Raise):
        if not in_excepthandler or not node.exc:
            node.cause = None

        if not in_excepthandler and not node.exc:
            return ast.Pass()

    if isinstance(node, ast.Lambda):
        # no annotation for lambda arguments
        for args in (node.args.posonlyargs, node.args.args, node.args.kwonlyargs):
            for arg in args:
                arg.annotation = None

        if node.args.vararg:
            node.args.vararg.annotation = None

        if node.args.kwarg:
            node.args.kwarg.annotation = None

    return node


class AstGenerator:
    def __init__(self, seed=0):
        self.rand = random.Random(seed)
        self.nodes = 0

    def cnd(self):
        return self.rand.choice([True, False])

    def generate(self, name: str, parents=(), depth=0):
        depth += 1
        self.nodes += 1

        if depth > 100:
            exit()

        stop = depth > 7 or self.nodes > 1000000

        info = get_info(name)

        if isinstance(info, NodeType):
            ranges = {}

            def range_for(child, attr_name):
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


import tempfile
import traceback

for seed in range(10000):
    print("seed:", seed)
    with tempfile.NamedTemporaryFile("w") as file:
        tree = AstGenerator(seed).generate("Module")
        ast.fix_missing_locations(tree)
        try:
            source = ast.unparse(tree)
            file.write(source)
            file.flush()
            compile(ast.unparse(tree), file.name, "exec")
        except Exception as e:
            print(ast.dump(tree, indent=2))
            print(source)
            traceback.print_exc()
            print("last seed:", seed)
            exit(1)
