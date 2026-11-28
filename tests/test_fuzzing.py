import ast
import sys
import threading
import unittest
from unittest.mock import patch

from .test_invalid_ast import AstIssue
from .test_invalid_ast import minimize_invalid_ast
from .test_invalid_ast import probe_invalid_ast


class TestAstFuzzing(unittest.TestCase):
    def test_probe_reports_checker_and_compiler_failures(self):
        tree = ast.parse("pass")
        for checker_accepts, compiles in (
            (False, True),
            (False, False),
            (True, False),
            (True, True),
        ):
            with self.subTest(checker_accepts=checker_accepts, compiles=compiles):
                with (
                    patch("tests.test_invalid_ast.generate_ast", return_value=tree),
                    patch(
                        "tests.test_invalid_ast.is_valid_ast",
                        return_value=checker_accepts,
                    ),
                    patch("tests.test_invalid_ast.does_compile", return_value=compiles),
                ):
                    issue = probe_invalid_ast(0)
                if checker_accepts and compiles:
                    self.assertIsNone(issue)
                else:
                    self.assertIsInstance(issue, AstIssue)
                    self.assertIs(issue.tree, tree)
                    self.assertEqual(issue.checker_accepts, checker_accepts)
                    self.assertEqual(issue.compiles, compiles)

    def test_checker_errors_are_not_reported_as_success(self):
        with (
            patch(
                "tests.test_invalid_ast.generate_ast", return_value=ast.parse("pass")
            ),
            patch(
                "tests.test_invalid_ast.is_valid_ast",
                side_effect=RuntimeError("checker bug"),
            ),
        ):
            with self.assertRaisesRegex(RuntimeError, "checker bug"):
                probe_invalid_ast(0)

    def test_minimization_preserves_a_compilable_checker_rejection(self):
        original = ast.parse("x = 1\npass")
        minimized = ast.parse("pass")
        invalid = ast.Module(body=[ast.Return(value=None), ast.Pass()], type_ignores=[])

        def accepts(tree, *args):
            return not any(isinstance(node, ast.Pass) for node in ast.walk(tree))

        def minimize(tree, predicate):
            self.assertIs(tree, original)
            self.assertFalse(predicate(ast.parse("x = 1")))
            self.assertFalse(predicate(invalid))
            self.assertTrue(predicate(minimized))
            return minimized

        with (
            patch("tests.test_invalid_ast.is_valid_ast", side_effect=accepts),
            patch("tests.test_invalid_ast.minimize_ast", side_effect=minimize),
        ):
            content = minimize_invalid_ast(0, AstIssue(original, False, True))

        self.assertIn("rejected by its checker", content)
        self.assertIn("# checker accepts: False", content)
        self.assertIn("# compiles: True", content)
        namespace = {}
        exec(content, namespace)
        self.assertEqual(ast.dump(namespace["tree"]), ast.dump(minimized))

    def test_minimization_preserves_an_accepted_compilation_failure(self):
        invalid = ast.Module(body=[ast.Return(value=None)], type_ignores=[])

        def minimize(tree, predicate):
            self.assertFalse(predicate(ast.Return(value=None)))
            self.assertFalse(predicate(ast.parse("pass")))
            self.assertTrue(predicate(tree))
            return tree

        with (
            patch("tests.test_invalid_ast.is_valid_ast", return_value=True),
            patch("tests.test_invalid_ast.minimize_ast", side_effect=minimize),
        ):
            content = minimize_invalid_ast(0, AstIssue(invalid, True, False))
        self.assertIn("# checker accepts: True", content)
        self.assertIn("# compiles: False", content)

    def test_quiet_worker_returns_a_minimizable_checker_rejection(self):
        # The CLI adjusts sys.path at import time; do not leak that into tests.
        with patch.object(sys, "path", sys.path.copy()):
            import find_new_issue as finder

        found = threading.Event()
        with (
            patch.object(finder, "_found", found),
            patch.object(finder, "kinds", ["invalid_ast"]),
            patch(
                "tests.test_invalid_ast.generate_ast", return_value=ast.parse("pass")
            ),
            patch("tests.test_invalid_ast.is_valid_ast", return_value=False),
        ):
            issue = finder.try_seed(0, quiet=True)
            self.assertIsNotNone(issue)
            self.assertEqual(issue.kind, "invalid_ast")
            self.assertIsInstance(issue.payload, AstIssue)
            self.assertTrue(found.is_set())
            content = finder.minimize_issue(issue)

        namespace = {}
        exec(content, namespace)
        self.assertIsInstance(namespace["tree"], ast.Module)
        self.assertIn("# checker accepts: False", content)
        self.assertIn("# compiles: True", content)
