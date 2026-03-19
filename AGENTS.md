# pysource-codegen — Agent Guide

## Project Overview

`pysource-codegen` generates random, syntactically valid Python source code.
Its primary use case is fuzz-testing tools that operate on Python source — formatters, linters, static analysers, etc.
The generated code can be compiled but should **not** be executed.

GitHub: https://github.com/15r10nk/pysource-codegen
License: MIT
Python support: 3.8 – 3.14 (CPython & PyPy)
Current version: 0.7.1

---

## Repository Layout

```
pysource_codegen/         # Main package
  __init__.py             # Public API: exports `generate`
  __main__.py             # CLI entry point (`pysource-codegen`)
  __about__.py            # Version metadata
  _codegen.py             # Top-level generate/is_valid_ast/check entry points
  _generator.py           # Core recursive AST generator (AstGenerator base class + NodeRef)
  _codegen_rules.py       # StdGenerator: all validity rules / probability_try / fix
  _checker.py             # AstChecker: deterministic replaying checker (used by is_valid_ast)
  _limits.py              # Runtime detection of f-string nesting limits
  _utils.py               # Helpers: ast_dump, unparse, equal_ast, walk_*, arguments …
  static_type_info.py     # Hand-written AST schema (NodeType / UnionNodeType / BuiltinNodeType)
  types.py                # Dataclasses for the three schema types
  ast_info.py             # get_info() – looks up static_type_info at runtime
  py.typed                # PEP 561 marker
  rules/
    rules_base.py         # RulesBase abstract base class
    legacy.py             # Placeholder Rules subclass

tests/
  test_valid_source.py    # Assert is_valid_ast(parse(file)) == True for every sample
  test_invalid_ast.py     # Assert is_valid_ast(tree) == does_compile(tree) for samples
  test_fix_nonlocal.py    # Tests for nonlocal / scoping fixes
  conftest.py             # pytest hooks; --generate-samples flag for producing new samples
  TestBase.py             # Base test class with addDetail / message helpers
  valid_source_samples/   # .py files that must parse and be accepted by is_valid_ast
  invalid_ast_samples/    # .py files defining `tree = …` with known-bad ASTs

find_new_issue.py         # Script to brute-force find seeds that trigger bugs
run_all.py                # Run tests across multiple Python versions
ai_coding_agent.py        # pydantic-ai agent that can run tests and edit source files
```

---

## Key Abstractions

### `NodeType` / `UnionNodeType` / `BuiltinNodeType`  (`types.py`, `static_type_info.py`)

The AST grammar is encoded as a hand-written dictionary in `static_type_info.py`.

- **`NodeType`** — a concrete AST node.
  `fields` maps `attr_name → (child_type_name, quantity)` where quantity is:
  - `""` — exactly one child
  - `"?"` — optional (may be `None`)
  - `"*"` — a list of zero or more children

- **`UnionNodeType`** — a named choice between several node type names (e.g. `"stmt"`, `"expr"`, `"_deleteTargets"`).

- **`BuiltinNodeType`** — a leaf value of kind `"identifier"`, `"int"`, `"string"`, or `"constant"`.

`get_info(type_name)` resolves a string to one of these three.

### `NodeRef`  (`_generator.py`)

A lightweight wrapper that tracks the path from the tree root to any node:

```
NodeRef(parent, parent_attr, parent_attr_index, node)
```

Key methods:
- `all_parents()` → `list[tuple[str, str]]` — the ancestor chain as `(NodeTypeName, attr_name)` pairs, used throughout as the `parents` argument.
- `relocate(tree)` — re-roots the same path into a different tree (used by `AstChecker`).
- `unknown_attr(attr, index=None)` — create a child ref whose node is not yet known (used during generation before the child is placed).
- `new_child(value, attr, index=None)` — create a child ref after placement.

### `AstGenerator`  (`_generator.py`)

Abstract base class for generation.  Subclasses override hooks:

| Method | Purpose |
|--------|---------|
| `probability_try(node, parents, child_name)` | Return weight for `child_name` at this position, or `raise Invalid` to forbid it |
| `probability(node, parents, child_name)` | Wraps `probability_try`, converts `Invalid` → 0 |
| `fix(node, parent, parents)` | Post-process a node after all children are placed |
| `fix_result(tree)` | Post-process the fully assembled tree |
| `same_length()` | Declare which attribute pairs must have the same list length (e.g. `Compare.ops` / `Compare.comparators`) |
| `min_attr_length(type_name, attr_name)` | Minimum list length for an attribute |
| `none_allowed(parent, parents)` | Whether a `?`-quantity field may be `None` here |
| `use()` | Guard hook for optional fix-up steps (mocked in tests to explore edge cases) |
| `_should_place_none(child_node_ref, quantity, parent_node, parents)` | Whether to place `None` for an optional field (overridden in `AstChecker`) |
| `attr_length_provider(parent_node)` | Returns a closure `(attr_name, stop) → int` for list lengths |

Generation dispatches to:
- `generate_NodeType` — instantiate the node, then recursively generate each field.
- `generate_UnionNodeType` — pick one option by weighted random (`rand.choices`) or deterministically when only one option has non-zero probability.
- `generate_BuiltinNodeType` — produce a leaf value (identifier, int, string, or constant).

### `StdGenerator`  (`_codegen_rules.py`)

The production subclass.  Contains all the rules that make the generated code compilable:
- `probability_try` — encodes ~500 lines of AST grammar constraints (scope, f-strings, delete targets, comprehension restrictions, match statements, …).
- `fix` — repairs `ctx` (Load/Store/Del), conversion flags, starred unpacking, unique argument names, nonlocal/global scoping, …
- `fix_result` — repairs the whole tree after generation (nonlocal hoisting, walrus scope, …).
- `same_length` — enforces same-length pairs for `Compare`, `Dict`, `MatchClass`, `MatchMapping`, `arguments`.

### `AstChecker`  (`_checker.py`)

A deterministic checker built on top of `StdGenerator`.  Given an existing `tree`, it "generates" by always choosing the same node as the target tree, then checks that the result equals the target.  This verifies that the tree satisfies all `StdGenerator` rules without randomness:

- `probability` returns 1 for the matching type, 0 for everything else.  If the match type has probability 0 according to `StdGenerator`, raises `_InvalidTree`.
- `attr_length_provider` reads lengths directly from the target tree, enforcing `same_length` constraints.
- `_should_place_none` checks whether the target field is actually `None`.
- `generate_BuiltinNodeType` copies the leaf value from the target.
- Invalid trees (wrong lengths, missing attributes, etc.) surface as `_InvalidTree`, `AttributeError`, or `IndexError` → `check()` returns `False`.

### `is_valid_ast`  (`_codegen.py`)

Runs both the legacy `StdGenerator.is_valid_ast` walk and the new `AstChecker.check`, cross-checks them, and returns the `AstChecker` result.

---

## Test Infrastructure

### Running tests

```bash
# Standard run (uses the project venv / hatch)
hatch run test

# Specific Python version
uvx -p 3.8.2 --with astunparse python -m unittest
uvx -p 3.15.0a6 python -m unittest

# Type checking (all supported versions)
hatch run types:check
```

> **Note:** Python < 3.9 requires the `astunparse` package (declared as a conditional dependency).

### Sample-based tests

- `tests/valid_source_samples/*.py` — each file contains a short Python snippet.  The test parses it and asserts `is_valid_ast(tree) == True`.
- `tests/invalid_ast_samples/*.py` — each file contains `tree = <ast literal>`.  The test asserts `is_valid_ast(tree) == does_compile(tree)` (invalid ASTs that fail `compile()` must also be rejected by the checker).

### Generating new samples

```bash
pytest --generate-samples
```

`conftest.py` will run `generate_invalid_ast` in a multiprocessing pool for 5 minutes and save any found bugs as new samples.

---

## Adding / Changing Rules

1. **Grammar constraints** go in `StdGenerator.probability_try` (`_codegen_rules.py`).  `raise Invalid` forbids a child; returning a positive float allows it.  The `inside()` helper checks the ancestor chain.

2. **Post-placement fixes** go in `StdGenerator.fix`.  Receives the node and its parent context.

3. **Whole-tree fixes** go in `StdGenerator.fix_result`.

4. **List-length constraints** go in `StdGenerator.same_length` (and in `AstChecker.attr_length_provider` which reads them automatically).

5. **New AST node types** must be added to `static_type_info.py` with the correct `NodeType` / `UnionNodeType` entries.  The `_deleteTargets` pseudo-union is an example of a synthetic union used to restrict which node types may appear in a specific position.

---

## Common Pitfalls

- **`parents` vs `node_ref`** — `parents` is `list[tuple[str, str]]` (the ancestor chain), `node_ref` is the corresponding `NodeRef`.  They must be kept in sync: `node_ref.all_parents() == parents` is asserted in `StdGenerator.probability_try`.  When passing a child `NodeRef` to `generate_impl`, use `node_ref.unknown_attr(attr_name, index)` so the child's `all_parents()` will equal `new_parents`.

- **Enumerate order** — `for i, e in enumerate(value)` (not `e, i`).

- **`AstChecker.rand`** — always raises `AssertionError`.  Any code path that calls `self.rand` in `AstChecker` is a bug.  Use `_should_place_none` or override the relevant `generate_*` method.

- **Python 3.8 / astunparse** — `ast.unparse` does not exist before 3.9.  The `_utils.py` conditional import handles this, but `astunparse` must be available at runtime on 3.8.

---

## CI / Tooling

- **Hatch** — build, test, and type-check environments.
- **mypy** — strict type checking across all supported Python versions via `hatch run types:check`.
- **commitizen** — conventional commits and changelog generation.
- **cogapp** — inline code generation in `*.md` files (`hatch run cog:update`).
