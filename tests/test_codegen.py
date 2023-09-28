import tempfile
import traceback

import pytest
from rich.console import Console
from rich.syntax import Syntax

from pysource_codegen import generate


@pytest.mark.parametrize("seed", list(range(50)))
def test_codegen(seed):
    with tempfile.NamedTemporaryFile("w", delete=False) as file:
        source = generate(seed)
        file.write(source)
        file.flush()
        try:
            compile(source, file.name, "exec")

        except Exception as e:
            if (
                isinstance(e, SyntaxError)
                and e.msg == "too many statically nested blocks"
            ):
                pytest.skip()

            console = Console()

            console.print(Syntax(source, "python", line_numbers=True, word_wrap=True))
            traceback.print_exc()

            raise
