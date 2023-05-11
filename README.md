# Introduction


`pysource_codegen` is able to generate random python code which can be compiled.
The compiled code should no be executed.

This is still a very early version, but it does its job.
It is general useful to test tools like formatters, linters or anything which operates on python code.

## Install:
``` bash
pip install pysource-codegen
```

## Usage:

The tool can be used over the CLI:

``` bash
pysource-codegen --seed 42
```

or as a library:

``` python
from pysource_codegen import generate

seed = 42
print(generate(seed))
```

You might find [pysource-minimize](https://github.com/15r10nk/pysource-minimize) also useful
to reduce the generated code which triggers your bug down to a minimal code snipped,
which can be used to fix the issue.

## Bugs found in other projects:

* https://github.com/psf/black/issues/3676
* https://github.com/psf/black/issues/3678
* https://github.com/psf/black/issues/3677

## Todo:

* [ ] refactor the existing code
* [ ] use probabilities for the ast-nodes from existing python code (use markov chains)
* [ ] support older python versions
* [ ] allow to customize the probabilities to generate code to test specific language features
