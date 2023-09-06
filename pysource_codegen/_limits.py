def calc_f_string_expr_limit():
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


def calc_f_string_format_limit():
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
