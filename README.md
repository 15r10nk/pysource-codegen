# Introduction


`pysource_codegen` is able to generate random python code which can be compiled by cpython.
This python code should no be executed.

This is still a very early version, but it does its job.

Install:
``` bash
pip install pysource-codegen
```

Usage:

The tool can be used over the CLI:

``` bash
pysource-codegen --help
```

or as a library:

```
from pysource_codegen import generate

seed=42
print(generate(seed))
```



Todo:

* refactor the existing code
* use probabilities for the ast-nodes from existing python code (use markov chains)
* support older python versions
* allow to customize the probabilities to generate code to test specific language features
