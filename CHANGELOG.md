## v0.5.0 (2023-11-29)

### Feat

- removed 3.7 support
- constant float, int and bytes values
- removed 3.7 support

### Fix

- a variable can not be nonlocal and global
- workaround for https://github.com/python/cpython/issues/111123
- correct handling of used names in SetComp
- check for yield in return-annotation in a inner function of an async function which returns a value
- use correct minimal length for lists of child nodes
- Starred expression inside AnnAssign target is not allowed
- correct handling of used names in DictComp
- an annotated varible can not be declared nonlocal
- global declaration of a used name in a return annotation is not allowed
- global declaration of a class in the current scope is not allowed
- **3.8**: use correct node types for Slices
- kwonlyargs and kw_defaults has to have the same size
- handle default arguments in the scope where the function is defined
- handle Slice and Starred in Subscript correctly
- **yield**: correct handling of code which is part of a function (yield inside decorator)
- handle MatchAs as name which can be used with global/nonlocal
- class variables can not be accessed by nonlocal from child scope
- correct handling of used names in ListComp
- **global**: check for used names in comprehension.iter
- **global**: use of names in annotations is not allowed before their global declaration
- **nonlocal**: do not search for assigned variables inside genarator expressions
- allow negative constants as match values
- allow all expression as match values
- handle wildcard with guard clause correct
- allow to match constants
- allow return with value in async function without yield, but inner generator function
- allow async GeneratorExp in non async code
- allow break in async for
- allow nonlocal definition of one variable twice
- allow global definition of one variable twice
- allow nonlocal of variables which are only deleted in the parent scope
- allow `nonlocal __class__` in methods
- allow Nonlocal in ClassDef
- support Slice ExtSlice and Index for 3.8 and 3.7
- allow Subscript as AnnAssign target
- allow yield inside lambda
- generate code like `del(a,[b,c])`
- generate correct AnnAssign
- allow raise at module level
- string constants issues
- allow continue outside of functions
- allow empty modules
- allow annotation of attribute assignments
- recreated poetry.lock

### Refactor

- created ast_dump
- removed the internal use of compile()

## v0.4.3 (2023-11-12)

### Fix

- remove upper bound from dependencies in pyproject.toml

## v0.4.2 (2023-10-07)

### Fix

- filter syntax warnings

## v0.4.1 (2023-10-01)

### Fix

- fix nonlocal/global handling

## v0.4.0 (2023-10-01)

### Feat

- 3.12 support

### Fix

- **3.7**: continue is not allowed in finally clause

### Refactor

- remove compile()

## v0.3.0 (2023-09-05)

## v0.2.0 (2023-08-05)

### Feat

- 3.7 support
- typing
- 3.8 support
- 3.9 support
- 3.10 support

### Fix

- typing & updated pre-commit checks

## v0.1.0 (2023-05-11)

### Feat

- added cli interface

### Fix

- changed propabilities to generate more expressions
