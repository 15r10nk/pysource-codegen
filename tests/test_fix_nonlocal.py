import ast
import sys
from pathlib import Path
from typing import Any

from pysource_codegen._codegen_rules import StdGenerator


sys.path.append(str(Path(__file__).parent.parent.parent / "pysource-minimize" / "src"))

try:
    from inline_snapshot import snapshot
except Exception:

    def snapshot(obj: Any = None) -> Any:
        return obj


from pysource_codegen._codegen import unparse
from pysource_codegen._utils import ast_dump

known_errors = snapshot(
    [
        "no binding for nonlocal 'x' found",
        "name 'x' is parameter and nonlocal",
        "name 'x' is used prior to nonlocal declaration",
        "name 'x' is assigned to before nonlocal declaration",
        "name 'x' is parameter and global",
        "name 'x' is assigned to before global declaration",
        "name 'x' is used prior to global declaration",
        "annotated name 'x' can't be global",
        "name 'x' is nonlocal and global",
        "annotated name 'x' can't be nonlocal",
        "nonlocal binding not allowed for type parameter 'x'",
        "annotated name 'name_3' can't be global",
        "name 'name_0' is used prior to global declaration",
    ]
)


def check_code(src: str, snapshot_value: Any) -> None:
    try:
        compile(src, "<string>", "exec")
    except SyntaxError as error:
        error_str = str(error)
        assert error_str.split(" (")[0] in known_errors
    else:
        assert False, "error expected"

    tree = ast.parse(src)

    print("original tree:")
    print(ast_dump(tree))
    print("original src:")
    print(src)
    print("error:", str(error_str))
    generator = StdGenerator()

    fixed_tree = generator.fix_nonlocal(tree)
    new_src = unparse(fixed_tree).strip() + "\n"

    print()
    print("transformed tree:")
    print(ast_dump(fixed_tree))
    print("transformed src:")
    print(new_src)

    compile(new_src, "<string>", "exec")

    assert new_src == snapshot_value


def test_global_0() -> None:
    check_code(
        """
def a(x):
    global x
    """,
        snapshot(
            """\
def a(x):
    pass
"""
        ),
    )


def test_global_1() -> None:
    check_code(
        """
def a():
    x = 0
    global x
    """,
        snapshot(
            """\
def a():
    x = 0
    pass
"""
        ),
    )


def test_global_2() -> None:
    check_code(
        """
def a():
    print(x)
    global x
    """,
        snapshot(
            """\
def a():
    print(x)
    pass
"""
        ),
    )


def test_global_3() -> None:
    check_code(
        """
def a():
    x:int
    global x
    """,
        snapshot(
            """\
def a():
    x: int
    pass
"""
        ),
    )


def test_global_4() -> None:
    check_code(
        """

def a():
    x=5
    def b():
        nonlocal x
        global x
    """,
        snapshot(
            """\
def a():
    x = 5

    def b():
        nonlocal x
        pass
"""
        ),
    )


def test_global_5() -> None:
    check_code(
        """
def name_4():
    global name_3
    name_3: int
    """,
        snapshot(
            """\
def name_4():
    global name_3
    pass
"""
        ),
    )


def test_nonlocal_0() -> None:
    check_code(
        """
def b():
    def a():
        nonlocal x
    """,
        snapshot(
            """\
def b():

    def a():
        pass
"""
        ),
    )


def test_nonlocal_1() -> None:
    check_code(
        """
def b():
    x=0
    def a(x):
        nonlocal x
    """,
        snapshot(
            """\
def b():
    x = 0

    def a(x):
        pass
"""
        ),
    )


def test_nonlocal_2() -> None:
    check_code(
        """
def b():
    x=0
    def a():
        print(x)
        nonlocal x
    """,
        snapshot(
            """\
def b():
    x = 0

    def a():
        print(x)
        pass
"""
        ),
    )


def test_nonlocal_3() -> None:
    check_code(
        """
def b():
    x=0
    def a():
        x=5
        nonlocal x
    """,
        snapshot(
            """\
def b():
    x = 0

    def a():
        x = 5
        pass
"""
        ),
    )


def test_nonlocal_4() -> None:
    check_code(
        """
def b():
    x=0
    def a():
        x:int
        nonlocal x
    """,
        snapshot(
            """\
def b():
    x = 0

    def a():
        x: int
        pass
"""
        ),
    )


def test_nonlocal_5() -> None:
    if sys.version_info >= (3, 12):
        check_code(
            """
def b():
    x=0
    def a[x:int]():
        nonlocal x
    """,
            snapshot(
                """\
def b():
    x = 0

    def a[x: int]():
        pass
"""
            ),
        )
