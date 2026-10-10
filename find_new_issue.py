# /// script
# dependencies = [
#   "ast-decompiler",
#   "rich",
# ]
#
# [tool.uv.sources]
# ast-decompiler = { path = "../ast_decompiler" }
# ///
from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import itertools
import multiprocessing.synchronize
import os
import subprocess
import sys
from concurrent.futures import FIRST_COMPLETED
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import wait
from dataclasses import dataclass
from pathlib import Path
from random import randrange
from typing import Any
from typing import Callable

from rich.progress import BarColumn
from rich.progress import MofNCompleteColumn
from rich.progress import Progress
from rich.progress import ProgressColumn
from rich.progress import SpinnerColumn
from rich.progress import TaskProgressColumn
from rich.progress import TextColumn
from rich.progress import TimeElapsedColumn
from rich.progress import TimeRemainingColumn
from rich.text import Text

sys.path.insert(1, str(Path(__file__).parent.parent / "ast_decompiler"))
sys.path.append(str(Path(__file__).parent.parent / "pysource-minimize" / "src"))

from tests.test_invalid_ast import minimize_invalid_ast
from tests.test_invalid_ast import probe_invalid_ast
from tests.test_valid_source import minimize_valid_source
from tests.test_valid_source import probe_valid_source


@dataclass
class Algorithm:
    probe: Callable[[int], object | None]
    minimize: Callable[[int, Any], str]


@dataclass
class FoundIssue:
    kind: str
    seed: int
    payload: Any


# Module-level so worker functions are picklable by ProcessPoolExecutor.
algorithms = {
    "invalid_ast": Algorithm(probe_invalid_ast, minimize_invalid_ast),
    "valid_source": Algorithm(probe_valid_source, minimize_valid_source),
}
kinds = sorted(algorithms)

# Initialised in the main process; replaced in each worker via _worker_init.
_found: multiprocessing.synchronize.Event = multiprocessing.Event()


def _worker_init(event: multiprocessing.synchronize.Event) -> None:
    global _found
    _found = event


def multiprocessing_context() -> multiprocessing.context.BaseContext:
    if "fork" in multiprocessing.get_all_start_methods():
        return multiprocessing.get_context("fork")
    return multiprocessing.get_context()


def try_seed(seed: int, quiet: bool = False) -> FoundIssue | None:
    if _found.is_set():
        return None
    kind = kinds[seed % len(kinds)]
    stdout = io.StringIO()
    stderr = io.StringIO()
    try:
        if quiet:
            stream_context = contextlib.redirect_stdout(stdout)
            error_context = contextlib.redirect_stderr(stderr)
        else:
            stream_context = contextlib.nullcontext()
            error_context = contextlib.nullcontext()
        with stream_context, error_context:
            result = algorithms[kind].probe(seed)
    except BaseException as e:
        output = stdout.getvalue() + stderr.getvalue()
        message = f"generation error for seed {seed}"
        if output:
            message += f"\nworker output:\n{output}"
        raise RuntimeError(message) from e

    if result is not None:
        _found.set()
        return FoundIssue(kind, seed, result)
    return None


def minimize_issue(issue: FoundIssue) -> str:
    return algorithms[issue.kind].minimize(issue.seed, issue.payload)


def minimize_issue_with_progress(issue: FoundIssue) -> str:
    stdout = io.StringIO()
    stderr = io.StringIO()
    with Progress(
        SpinnerColumn(),
        TextColumn(f"[bold blue]minimize {issue.kind} seed {issue.seed}"),
        TimeElapsedColumn(),
    ) as progress:
        progress.add_task("", total=None)
        try:
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                return minimize_issue(issue)
        except BaseException:
            output = stdout.getvalue() + stderr.getvalue()
            if output:
                print(output)
            raise


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, help="Test only one seed value")
    parser.add_argument("--force", action="store_true", help="skip safety tests")
    parser.add_argument(
        "--workers", type=int, default=os.cpu_count(), help="Number of parallel workers"
    )
    parser.add_argument(
        "--num-seeds",
        type=int,
        default=None,
        help="Total number of seeds to test (default: unlimited)",
    )
    args = parser.parse_args()

    if not args.force:
        dirty = subprocess.run(
            ["git", "status", "--porcelain"], capture_output=True, text=True
        )
        if dirty.stdout.strip():
            print("Uncommitted changes detected — commit or stash them first.")
            print(dirty.stdout)
            raise SystemExit(1)

        print("Running run_all.py to check for existing bugs...")
        pre_check = subprocess.run(["uv", "run", "run_all.py"])
        if pre_check.returncode != 0:
            print("Existing bugs detected — fix them before searching for new ones.")
            raise SystemExit(pre_check.returncode)

    def save_sample(kind: str, content: str) -> None:
        sample_dir = Path(__file__).parent / "tests" / f"{kind}_samples"
        name = sample_dir / f"{hashlib.sha256(content.encode()).hexdigest()}.py"
        name.write_text(content)
        subprocess.run(["git", "add", str(name)], check=True)
        print(content)
        print(f"Saved: {name}")

    if args.seed is not None:
        print(f"Testing seed {args.seed}")
        issue = try_seed(args.seed)
        if issue:
            content = minimize_issue(issue)
            save_sample(issue.kind, content)
        exit()
    else:

        class SeedsPerSecColumn(ProgressColumn):
            def render(self, task) -> Text:  # type: ignore[override]
                speed = task.speed
                if speed is None:
                    return Text("? seeds/s", style="green")
                return Text(f"{speed:.0f} seeds/s", style="green")

        def random_seeds():
            while True:
                yield randrange(10_000_000_000)

        def progress_columns():
            if args.num_seeds is None:
                return (
                    SpinnerColumn(),
                    TextColumn("[bold blue]find-new-issue"),
                    TextColumn("[progress.completed]{task.completed} seeds"),
                    TextColumn("{task.fields[active]}/{task.fields[workers]} active"),
                    TimeElapsedColumn(),
                    SeedsPerSecColumn(),
                )
            return (
                SpinnerColumn(),
                TextColumn("[bold blue]find-new-issue"),
                BarColumn(),
                MofNCompleteColumn(),
                TaskProgressColumn(),
                TimeRemainingColumn(),
                TextColumn("{task.fields[active]}/{task.fields[workers]} active"),
                SeedsPerSecColumn(),
            )

        mp_context = multiprocessing_context()
        found = mp_context.Event()
        issue: FoundIssue | None = None
        worker_count = max(args.workers or 1, 1)

        with Progress(*progress_columns()) as progress:
            task = progress.add_task(
                "", total=args.num_seeds, active=0, workers=worker_count
            )

            executor = ProcessPoolExecutor(
                max_workers=worker_count,
                mp_context=mp_context,
                initializer=_worker_init,
                initargs=(found,),
            )
            interrupted = False
            failed = False
            try:
                seed_stream = itertools.islice(random_seeds(), args.num_seeds)
                pending = {}

                def submit_seed(seed: int) -> None:
                    pending[executor.submit(try_seed, seed, True)] = seed
                    progress.update(task, active=len(pending))

                for seed in itertools.islice(seed_stream, worker_count):
                    submit_seed(seed)

                try:
                    while pending:
                        done, _ = wait(pending, return_when=FIRST_COMPLETED)
                        for future in done:
                            pending.pop(future)
                            try:
                                result = future.result()
                            except BaseException:
                                failed = True
                                found.set()
                                progress.advance(task)
                                progress.update(task, active=len(pending))
                                for pending_future in pending:
                                    pending_future.cancel()
                                pending.clear()
                                raise
                            else:
                                progress.advance(task)
                                progress.update(task, active=len(pending))
                            if issue := result:
                                found.set()
                                for pending_future in pending:
                                    pending_future.cancel()
                                pending.clear()
                                progress.update(task, active=0)
                                break
                            if (s := next(seed_stream, None)) is not None:
                                submit_seed(s)
                except KeyboardInterrupt:
                    found.set()  # signal workers to stop early
                    interrupted = True
                    progress.stop()
                    print("\nInterrupted.")
                    raise SystemExit(1)
            finally:
                if (issue is not None or interrupted or failed) and hasattr(
                    executor, "terminate_workers"
                ):
                    executor.terminate_workers()
                else:
                    executor.shutdown(wait=False, cancel_futures=True)

        if issue:
            content = minimize_issue_with_progress(issue)
            save_sample(issue.kind, content)
