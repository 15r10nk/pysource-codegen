

from pysource_codegen import AstGenerator,generate
import ast

import tempfile
import traceback
import pytest
from rich.syntax import Syntax
from rich.console import Console
import subprocess as sp


@pytest.mark.parametrize("seed",list(range(1000)))
def test_codegen(seed):
    with tempfile.NamedTemporaryFile("w",delete=False) as file:
        try:
            source=generate(seed)
            file.write(source)
            file.flush()
            compile(source, file.name, "exec")
            #sp.check_call(["black",file.name])

        except Exception as e:
            if isinstance(e,SyntaxError) and e.msg=="too many statically nested blocks":
                pytest.skip()
                
            console=Console()

            if 0:
                console.print(Syntax(source,"python",line_numbers=True,word_wrap=True))
                traceback.print_exc()
            raise
