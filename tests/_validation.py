import ast
import copy
import sys
import warnings
from typing import Callable

from pysource_codegen._utils import equal_ast
from pysource_codegen._utils import unparse


def _normalize_roundtrip(tree: ast.Module) -> ast.Module:
    """Keep the existing structural comparison independent of quote spelling."""
    normalized = copy.deepcopy(tree)
    for node in ast.walk(normalized):
        if hasattr(node, "type_ignores"):
            node.type_ignores = []
        if isinstance(node, ast.Constant):
            if isinstance(node.value, str):
                node.value = node.value.replace("'", "_").replace('"', "_")
            elif isinstance(node.value, bytes):
                node.value = node.value.replace(b"'", b"_").replace(b'"', b"_")
    if sys.version_info >= (3, 14):
        for node in ast.walk(normalized):
            if isinstance(node, ast.Interpolation):
                formatted = ast.JoinedStr(
                    [
                        ast.FormattedValue(
                            value=node.value, conversion=-1, format_spec=None
                        )
                    ]
                )
                source = unparse(formatted)
                node.str = (
                    source[5:-4]
                    if source.startswith(("f'''", 'f"""'))
                    else source[3:-2]
                )
    return normalized


def is_valid_python(
    tree: ast.Module,
    add_detail: Callable[..., None] = lambda *items: None,
) -> bool:
    """Compile AST and source, and require a normalized AST round-trip.

    This predicate is shared by both sample kinds and both fuzzing paths.
    Generated Python code is never executed.
    """
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", SyntaxWarning)
            normalized = _normalize_roundtrip(tree)
            # Parse before compiling raw ASTs: malformed trees can crash older
            # CPython compilers instead of raising a Python exception.
            if not equal_ast(ast.parse(unparse(normalized)), normalized, add_detail):
                return False

            if sys.version_info >= (3, 14):
                for node in ast.walk(tree):
                    if isinstance(node, ast.AnnAssign) and not node.simple:
                        # CPython can omit validation of an unevaluated annotation.
                        # Check the same annotation in an evaluated position too.
                        annotation = ast.Module(
                            body=[
                                ast.AnnAssign(
                                    target=ast.Name(id="a", ctx=ast.Store()),
                                    annotation=copy.deepcopy(node.annotation),
                                    value=ast.Constant(value=None),
                                    simple=1,
                                )
                            ],
                            type_ignores=[],
                        )
                        if not is_valid_python(annotation, add_detail):
                            add_detail("cannot compile annotation", node.annotation)
                            return False

            for node in ast.walk(tree):
                if isinstance(node, ast.BoolOp) and len(node.values) < 2:
                    return False
                if not isinstance(node, ast.JoinedStr) and any(
                    isinstance(child, ast.FormattedValue)
                    for child in ast.iter_child_nodes(node)
                ):
                    return False
            compile(unparse(tree), "<source>", "exec", dont_inherit=True)
            compile(ast.fix_missing_locations(tree), "<ast>", "exec", dont_inherit=True)
    except Exception as error:
        add_detail(type(error).__name__ + ":", error)
        return False
    return True
