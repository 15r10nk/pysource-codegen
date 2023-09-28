import ast
import sys

from inline_snapshot import snapshot

from pysource_codegen._codegen import fix_nonlocal
from pysource_codegen._codegen import unparse

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


def check_code(src, snapshot_value):
    try:
        compile(src, "<string>", "exec")
    except SyntaxError as error:
        error_str = str(error)
        assert error_str.split(" (")[0] in known_errors
    else:
        assert False, "error expected"

    tree = ast.parse(src)

    print("original tree:")
    print(ast.dump(tree, **(dict(indent=2) if sys.version_info >= (3, 9) else {})))
    print("original src:")
    print(src)
    print("error:", str(error_str))

    tree = fix_nonlocal(tree)
    new_src = unparse(tree).strip() + "\n"

    print()
    print("transformed tree:")
    print(ast.dump(tree, **(dict(indent=2) if sys.version_info >= (3, 9) else {})))
    print("transformed src:")
    print(new_src)

    compile(new_src, "<string>", "exec")

    assert new_src == snapshot_value


def test_global():
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


def test_nonlocal():
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
