[![pypi version](https://img.shields.io/pypi/v/pysource-codegen.svg)](https://pypi.org/project/pysource-codegen/)
![Python Versions](https://img.shields.io/pypi/pyversions/pysource-codegen)
![PyPI - Downloads](https://img.shields.io/pypi/dw/pysource-codegen)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/15r10nk)](https://github.com/sponsors/15r10nk)

# Introduction


`pysource_codegen` is able to generate random python code which can be compiled.
The compiled code should not be executed.

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

``` python
from pysource_codegen import generate
from pysource_minimize import minimize


def contains_bug(code):
    """
    returns True if the code triggers a bug and False otherwise
    """
    try:
        test_something_with(code)  # might throw

        if "bug" in code:  # maybe other checks
            return True
    except:
        return True
    return False


def find_issue():
    for seed in range(0, 10000):
        code = generate(seed)

        if contains_bug(code):
            new_code = minimize(code, contains_bug)

            print("the following code triggers a bug")
            print(new_code)

            return


find_issue()
```


## Bugs found in other projects:

### black

* https://github.com/psf/black/issues/3676
* https://github.com/psf/black/issues/3678
* https://github.com/psf/black/issues/3677

### cpython

* https://github.com/python/cpython/issues/109219
* https://github.com/python/cpython/issues/109823
* https://github.com/python/cpython/issues/109719
* https://github.com/python/cpython/issues/109627
* https://github.com/python/cpython/issues/109219
* https://github.com/python/cpython/issues/109118
* https://github.com/python/cpython/issues/109114

## Todo:

* [ ] refactor the existing code
* [ ] use probabilities for the ast-nodes from existing python code (use markov chains)
* [x] support older python versions
* [ ] allow to customize the probabilities to generate code to test specific language features
* [ ] [hypothesis](https://hypothesis.readthedocs.io/en/latest/) support
