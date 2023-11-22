import ast
import sys

from .types import BuiltinNodeType
from .types import NodeType
from .types import UnionNodeType

assert sys.version_info >= (3, 8)

type_infos = {
    "Delete": NodeType(
        fields={"targets": ("_deleteTargets", "*")}, ast_type=ast.Delete
    ),
    "expr": UnionNodeType(
        options=[
            "BoolOp",
            "NamedExpr",
            "BinOp",
            "UnaryOp",
            "Lambda",
            "IfExp",
            "Dict",
            "Set",
            "ListComp",
            "SetComp",
            "DictComp",
            "GeneratorExp",
            "Await",
            "Yield",
            "YieldFrom",
            "Compare",
            "Call",
            "FormattedValue",
            "JoinedStr",
            "Constant",
            "Attribute",
            "Subscript",
            "Starred",
            "Name",
            "List",
            "Tuple",
        ]
    ),
    "BoolOp": NodeType(
        fields={"op": ("boolop", ""), "values": ("expr", "*")}, ast_type=ast.BoolOp
    ),
    "boolop": UnionNodeType(options=["And", "Or"]),
    "And": NodeType(fields={}, ast_type=ast.And),
    "Or": NodeType(fields={}, ast_type=ast.Or),
    "NamedExpr": NodeType(
        fields={"target": ("expr", ""), "value": ("expr", "")}, ast_type=ast.NamedExpr
    ),
    "BinOp": NodeType(
        fields={"left": ("expr", ""), "op": ("operator", ""), "right": ("expr", "")},
        ast_type=ast.BinOp,
    ),
    "operator": UnionNodeType(
        options=[
            "Add",
            "Sub",
            "Mult",
            "MatMult",
            "Div",
            "Mod",
            "Pow",
            "LShift",
            "RShift",
            "BitOr",
            "BitXor",
            "BitAnd",
            "FloorDiv",
        ]
    ),
    "Add": NodeType(fields={}, ast_type=ast.Add),
    "Sub": NodeType(fields={}, ast_type=ast.Sub),
    "Mult": NodeType(fields={}, ast_type=ast.Mult),
    "MatMult": NodeType(fields={}, ast_type=ast.MatMult),
    "Div": NodeType(fields={}, ast_type=ast.Div),
    "Mod": NodeType(fields={}, ast_type=ast.Mod),
    "Pow": NodeType(fields={}, ast_type=ast.Pow),
    "LShift": NodeType(fields={}, ast_type=ast.LShift),
    "RShift": NodeType(fields={}, ast_type=ast.RShift),
    "BitOr": NodeType(fields={}, ast_type=ast.BitOr),
    "BitXor": NodeType(fields={}, ast_type=ast.BitXor),
    "BitAnd": NodeType(fields={}, ast_type=ast.BitAnd),
    "FloorDiv": NodeType(fields={}, ast_type=ast.FloorDiv),
    "UnaryOp": NodeType(
        fields={"op": ("unaryop", ""), "operand": ("expr", "")}, ast_type=ast.UnaryOp
    ),
    "unaryop": UnionNodeType(options=["Invert", "Not", "UAdd", "USub"]),
    "Invert": NodeType(fields={}, ast_type=ast.Invert),
    "Not": NodeType(fields={}, ast_type=ast.Not),
    "UAdd": NodeType(fields={}, ast_type=ast.UAdd),
    "USub": NodeType(fields={}, ast_type=ast.USub),
    "Lambda": NodeType(
        fields={"args": ("arguments", ""), "body": ("expr", "")}, ast_type=ast.Lambda
    ),
    "arguments": NodeType(
        fields={
            "posonlyargs": ("arg", "*"),
            "args": ("arg", "*"),
            "vararg": ("arg", "?"),
            "kwonlyargs": ("arg", "*"),
            "kw_defaults": ("expr", "*"),
            "kwarg": ("arg", "?"),
            "defaults": ("expr", "*"),
        },
        ast_type=ast.arguments,
    ),
    "arg": NodeType(
        fields={
            "arg": ("identifier", ""),
            "annotation": ("expr", "?"),
            "type_comment": ("string", "?"),
        },
        ast_type=ast.arg,
    ),
    "identifier": BuiltinNodeType(kind="identifier"),
    "string": BuiltinNodeType(kind="string"),
    "IfExp": NodeType(
        fields={"test": ("expr", ""), "body": ("expr", ""), "orelse": ("expr", "")},
        ast_type=ast.IfExp,
    ),
    "Dict": NodeType(
        fields={"keys": ("expr", "*"), "values": ("expr", "*")}, ast_type=ast.Dict
    ),
    "Set": NodeType(fields={"elts": ("expr", "*")}, ast_type=ast.Set),
    "ListComp": NodeType(
        fields={"elt": ("expr", ""), "generators": ("comprehension", "*")},
        ast_type=ast.ListComp,
    ),
    "comprehension": NodeType(
        fields={
            "target": ("expr", ""),
            "iter": ("expr", ""),
            "ifs": ("expr", "*"),
            "is_async": ("int", ""),
        },
        ast_type=ast.comprehension,
    ),
    "int": BuiltinNodeType(kind="int"),
    "SetComp": NodeType(
        fields={"elt": ("expr", ""), "generators": ("comprehension", "*")},
        ast_type=ast.SetComp,
    ),
    "DictComp": NodeType(
        fields={
            "key": ("expr", ""),
            "value": ("expr", ""),
            "generators": ("comprehension", "*"),
        },
        ast_type=ast.DictComp,
    ),
    "GeneratorExp": NodeType(
        fields={"elt": ("expr", ""), "generators": ("comprehension", "*")},
        ast_type=ast.GeneratorExp,
    ),
    "Await": NodeType(fields={"value": ("expr", "")}, ast_type=ast.Await),
    "Yield": NodeType(fields={"value": ("expr", "?")}, ast_type=ast.Yield),
    "YieldFrom": NodeType(fields={"value": ("expr", "")}, ast_type=ast.YieldFrom),
    "Compare": NodeType(
        fields={
            "left": ("expr", ""),
            "ops": ("cmpop", "*"),
            "comparators": ("expr", "*"),
        },
        ast_type=ast.Compare,
    ),
    "cmpop": UnionNodeType(
        options=["Eq", "NotEq", "Lt", "LtE", "Gt", "GtE", "Is", "IsNot", "In", "NotIn"]
    ),
    "Eq": NodeType(fields={}, ast_type=ast.Eq),
    "NotEq": NodeType(fields={}, ast_type=ast.NotEq),
    "Lt": NodeType(fields={}, ast_type=ast.Lt),
    "LtE": NodeType(fields={}, ast_type=ast.LtE),
    "Gt": NodeType(fields={}, ast_type=ast.Gt),
    "GtE": NodeType(fields={}, ast_type=ast.GtE),
    "Is": NodeType(fields={}, ast_type=ast.Is),
    "IsNot": NodeType(fields={}, ast_type=ast.IsNot),
    "In": NodeType(fields={}, ast_type=ast.In),
    "NotIn": NodeType(fields={}, ast_type=ast.NotIn),
    "Call": NodeType(
        fields={
            "func": ("expr", ""),
            "args": ("expr", "*"),
            "keywords": ("keyword", "*"),
        },
        ast_type=ast.Call,
    ),
    "keyword": NodeType(
        fields={"arg": ("identifier", "?"), "value": ("expr", "")}, ast_type=ast.keyword
    ),
    "FormattedValue": NodeType(
        fields={
            "value": ("expr", ""),
            "conversion": ("int", "?"),
            "format_spec": ("expr", "?"),
        },
        ast_type=ast.FormattedValue,
    ),
    "JoinedStr": NodeType(fields={"values": ("expr", "*")}, ast_type=ast.JoinedStr),
    "Constant": NodeType(
        fields={"value": ("constant", ""), "kind": ("string", "?")},
        ast_type=ast.Constant,
    ),
    "constant": BuiltinNodeType(kind="constant"),
    "Attribute": NodeType(
        fields={
            "value": ("expr", ""),
            "attr": ("identifier", ""),
            "ctx": ("expr_context", ""),
        },
        ast_type=ast.Attribute,
    ),
    "expr_context": UnionNodeType(options=["Load", "Store", "Del"]),
    "Load": NodeType(fields={}, ast_type=ast.Load),
    "Store": NodeType(fields={}, ast_type=ast.Store),
    "Del": NodeType(fields={}, ast_type=ast.Del),
    "Subscript": NodeType(
        fields={
            "value": ("expr", ""),
            "slice": ("slice", ""),
            "ctx": ("expr_context", ""),
        },
        ast_type=ast.Subscript,
    ),
    "Starred": NodeType(
        fields={"value": ("expr", ""), "ctx": ("expr_context", "")},
        ast_type=ast.Starred,
    ),
    "Name": NodeType(
        fields={"id": ("identifier", ""), "ctx": ("expr_context", "")},
        ast_type=ast.Name,
    ),
    "List": NodeType(
        fields={"elts": ("expr", "*"), "ctx": ("expr_context", "")}, ast_type=ast.List
    ),
    "Tuple": NodeType(
        fields={"elts": ("expr", "*"), "ctx": ("expr_context", "")}, ast_type=ast.Tuple
    ),
    "slice": UnionNodeType(options=["Slice", "ExtSlice", "Index"]),
    "Slice": NodeType(
        fields={"lower": ("expr", "?"), "upper": ("expr", "?"), "step": ("expr", "?")},
        ast_type=ast.Slice,
    ),
    "ExtSlice": NodeType(
        fields={"dims": ("slice", "*")},
        ast_type=ast.ExtSlice,
    ),
    "Index": NodeType(
        fields={"value": ("expr", "")},
        ast_type=ast.Index,
    ),
    "_deleteTargets": UnionNodeType(options=["Name", "Attribute", "Subscript"]),
    "Module": NodeType(
        fields={"body": ("stmt", "*"), "type_ignores": ("type_ignore", "*")},
        ast_type=ast.Module,
    ),
    "stmt": UnionNodeType(
        options=[
            "FunctionDef",
            "AsyncFunctionDef",
            "ClassDef",
            "Return",
            "Delete",
            "Assign",
            "AugAssign",
            "AnnAssign",
            "For",
            "AsyncFor",
            "While",
            "If",
            "With",
            "AsyncWith",
            "Raise",
            "Try",
            "Assert",
            "Import",
            "ImportFrom",
            "Global",
            "Nonlocal",
            "Expr",
            "Pass",
            "Break",
            "Continue",
        ]
    ),
    "FunctionDef": NodeType(
        fields={
            "name": ("identifier", ""),
            "args": ("arguments", ""),
            "body": ("stmt", "*"),
            "decorator_list": ("expr", "*"),
            "returns": ("expr", "?"),
            "type_comment": ("string", "?"),
        },
        ast_type=ast.FunctionDef,
    ),
    "AsyncFunctionDef": NodeType(
        fields={
            "name": ("identifier", ""),
            "args": ("arguments", ""),
            "body": ("stmt", "*"),
            "decorator_list": ("expr", "*"),
            "returns": ("expr", "?"),
            "type_comment": ("string", "?"),
        },
        ast_type=ast.AsyncFunctionDef,
    ),
    "ClassDef": NodeType(
        fields={
            "name": ("identifier", ""),
            "bases": ("expr", "*"),
            "keywords": ("keyword", "*"),
            "body": ("stmt", "*"),
            "decorator_list": ("expr", "*"),
        },
        ast_type=ast.ClassDef,
    ),
    "Return": NodeType(fields={"value": ("expr", "?")}, ast_type=ast.Return),
    "Assign": NodeType(
        fields={
            "targets": ("expr", "*"),
            "value": ("expr", ""),
            "type_comment": ("string", "?"),
        },
        ast_type=ast.Assign,
    ),
    "AugAssign": NodeType(
        fields={"target": ("expr", ""), "op": ("operator", ""), "value": ("expr", "")},
        ast_type=ast.AugAssign,
    ),
    "AnnAssign": NodeType(
        fields={
            "target": ("expr", ""),
            "annotation": ("expr", ""),
            "value": ("expr", "?"),
            "simple": ("int", ""),
        },
        ast_type=ast.AnnAssign,
    ),
    "For": NodeType(
        fields={
            "target": ("expr", ""),
            "iter": ("expr", ""),
            "body": ("stmt", "*"),
            "orelse": ("stmt", "*"),
            "type_comment": ("string", "?"),
        },
        ast_type=ast.For,
    ),
    "AsyncFor": NodeType(
        fields={
            "target": ("expr", ""),
            "iter": ("expr", ""),
            "body": ("stmt", "*"),
            "orelse": ("stmt", "*"),
            "type_comment": ("string", "?"),
        },
        ast_type=ast.AsyncFor,
    ),
    "While": NodeType(
        fields={"test": ("expr", ""), "body": ("stmt", "*"), "orelse": ("stmt", "*")},
        ast_type=ast.While,
    ),
    "If": NodeType(
        fields={"test": ("expr", ""), "body": ("stmt", "*"), "orelse": ("stmt", "*")},
        ast_type=ast.If,
    ),
    "With": NodeType(
        fields={
            "items": ("withitem", "*"),
            "body": ("stmt", "*"),
            "type_comment": ("string", "?"),
        },
        ast_type=ast.With,
    ),
    "withitem": NodeType(
        fields={"context_expr": ("expr", ""), "optional_vars": ("expr", "?")},
        ast_type=ast.withitem,
    ),
    "AsyncWith": NodeType(
        fields={
            "items": ("withitem", "*"),
            "body": ("stmt", "*"),
            "type_comment": ("string", "?"),
        },
        ast_type=ast.AsyncWith,
    ),
    "Raise": NodeType(
        fields={"exc": ("expr", "?"), "cause": ("expr", "?")}, ast_type=ast.Raise
    ),
    "Try": NodeType(
        fields={
            "body": ("stmt", "*"),
            "handlers": ("excepthandler", "*"),
            "orelse": ("stmt", "*"),
            "finalbody": ("stmt", "*"),
        },
        ast_type=ast.Try,
    ),
    "excepthandler": UnionNodeType(options=["ExceptHandler"]),
    "ExceptHandler": NodeType(
        fields={
            "type": ("expr", "?"),
            "name": ("identifier", "?"),
            "body": ("stmt", "*"),
        },
        ast_type=ast.ExceptHandler,
    ),
    "Assert": NodeType(
        fields={"test": ("expr", ""), "msg": ("expr", "?")}, ast_type=ast.Assert
    ),
    "Import": NodeType(fields={"names": ("alias", "*")}, ast_type=ast.Import),
    "alias": NodeType(
        fields={"name": ("identifier", ""), "asname": ("identifier", "?")},
        ast_type=ast.alias,
    ),
    "ImportFrom": NodeType(
        fields={
            "module": ("identifier", "?"),
            "names": ("alias", "*"),
            "level": ("int", "?"),
        },
        ast_type=ast.ImportFrom,
    ),
    "Global": NodeType(fields={"names": ("identifier", "*")}, ast_type=ast.Global),
    "Nonlocal": NodeType(fields={"names": ("identifier", "*")}, ast_type=ast.Nonlocal),
    "Expr": NodeType(fields={"value": ("expr", "")}, ast_type=ast.Expr),
    "Pass": NodeType(fields={}, ast_type=ast.Pass),
    "Break": NodeType(fields={}, ast_type=ast.Break),
    "Continue": NodeType(fields={}, ast_type=ast.Continue),
    "type_ignore": UnionNodeType(options=["TypeIgnore"]),
    "TypeIgnore": NodeType(
        fields={"lineno": ("int", ""), "tag": ("string", "")}, ast_type=ast.TypeIgnore
    ),
}
