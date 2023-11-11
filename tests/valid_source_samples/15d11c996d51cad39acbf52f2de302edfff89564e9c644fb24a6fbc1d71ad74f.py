def _get_assertion_exprs():
    lines: List = []

    def _write_and_reset():
        nonlocal lines
