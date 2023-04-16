

from pysource_codegen import AstGenerator
import ast

import tempfile
import traceback
import pytest
from rich.syntax import Syntax
from rich.console import Console


@pytest.mark.parametrize("seed",list(range(1000)))
def test_codegen(seed):
    with tempfile.NamedTemporaryFile("w") as file:
        tree = AstGenerator(seed).generate("Module")
        ast.fix_missing_locations(tree)
        try:
            source = ast.unparse(tree)
            file.write(source)
            file.flush()
            compile(ast.unparse(tree), file.name, "exec")
        except Exception as e:
            console=Console()
            console.print(ast.dump(tree, indent=2))

            console.print(Syntax(source,"python",line_numbers=True))

            traceback.print_exc()
            print("last seed:", seed)
            exit(1)
