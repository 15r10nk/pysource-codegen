

from pysource_codegen import AstGenerator
import ast

import tempfile
import traceback
import pytest

@pytest.mark.parameterize("seed",range(1000))
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
            print(ast.dump(tree, indent=2))
            print(source)
            traceback.print_exc()
            print("last seed:", seed)
            exit(1)
