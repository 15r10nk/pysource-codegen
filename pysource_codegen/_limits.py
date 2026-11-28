import ast
import sys


def has_template_not_equal_parser_bug() -> bool:
    if sys.version_info < (3, 14):
        return False
    tree = ast.parse("t'{0 != 0:}'", mode="eval")
    assert isinstance(tree.body, ast.TemplateStr)
    interpolation = tree.body.values[0]
    assert isinstance(interpolation, ast.Interpolation)
    return interpolation.str != "0 != 0"


template_not_equal_parser_bug = has_template_not_equal_parser_bug()


def calc_f_string_expr_limit() -> int:
    n = 0
    s = "1"
    while True:
        for q in ("'", '"', '"""', "'''"):
            ns = "f" + q + "{" + s + "}" + q

            try:
                eval(ns)
                s = ns
                break
            except:
                continue
        else:
            return n
        n += 1


def calc_f_string_format_limit() -> int:
    n = 0
    s = "{1}"
    while True:
        s = "{2:" + s + "}"

        try:
            eval(f"f'{s}'")
        except:
            break
        n += 1

    return n


f_string_expr_limit = calc_f_string_expr_limit()
f_string_format_limit = calc_f_string_format_limit()
