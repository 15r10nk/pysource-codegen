# /// script
# dependencies = [
#   "ast-decompiler",
#   "rich",
# ]
#
# [tool.uv.sources]
# ast-decompiler = { path = "vendor/ast_decompiler" }
# ///
from __future__ import annotations

import argparse
import hashlib
import itertools
import multiprocessing.synchronize
import os
import subprocess
import sys
from concurrent.futures import FIRST_COMPLETED
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import wait
from pathlib import Path
from random import randrange

from rich.progress import BarColumn
from rich.progress import MofNCompleteColumn
from rich.progress import Progress
from rich.progress import ProgressColumn
from rich.progress import SpinnerColumn
from rich.progress import TaskProgressColumn
from rich.progress import TextColumn
from rich.progress import TimeRemainingColumn
from rich.text import Text

sys.path.insert(1, str(Path(__file__).parent / "vendor" / "ast_decompiler"))

from tests.test_invalid_ast import generate_invalid_ast
from tests.test_valid_source import generate_valid_source

# Module-level so worker functions are picklable by ProcessPoolExecutor.
generators = {
    "invalid_ast": generate_invalid_ast,
    "valid_source": generate_valid_source,
}
kinds = sorted(generators)

# Initialised in the main process; replaced in each worker via _worker_init.
_found: multiprocessing.synchronize.Event = multiprocessing.Event()


def _worker_init(event: multiprocessing.synchronize.Event) -> None:
    global _found
    _found = event


def try_seed(i: int) -> tuple[str, str] | None:
    if _found.is_set():
        return None
    kind = kinds[i % len(kinds)]
    try:
        result = generators[kind](i)
    except BaseException as e:
        raise RuntimeError(f"generation error for seed {i}") from e

    if result and result is not True:  # True = early-exit (generation bug), no sample
        _found.set()
        return (kind, result)
    return None


if __name__ == "__main__":
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

    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, help="Test only one seed value")
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

    def save_sample(kind: str, content: str) -> None:
        sample_dir = Path(__file__).parent / "tests" / f"{kind}_samples"
        name = sample_dir / f"{hashlib.sha256(content.encode()).hexdigest()}.py"
        name.write_text(content)
        subprocess.run(["git", "add", str(name)], check=True)
        print(content)
        print(f"Saved: {name}")

    if args.seed is not None:
        print(f"Testing seed {args.seed}")
        result = try_seed(args.seed)
        if result:
            kind, content = result
            save_sample(kind, content)
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

        found = multiprocessing.Event()

        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]find-new-issue"),
            BarColumn(),
            MofNCompleteColumn(),
            TaskProgressColumn(),
            TimeRemainingColumn(),
            SeedsPerSecColumn(),
        ) as progress:
            task = progress.add_task("", total=args.num_seeds)

            with ProcessPoolExecutor(
                max_workers=args.workers,
                initializer=_worker_init,
                initargs=(found,),
            ) as executor:
                seed_stream = itertools.islice(random_seeds(), args.num_seeds)
                pending = {
                    executor.submit(try_seed, s)
                    for s in itertools.islice(seed_stream, args.workers)
                }
                try:
                    while pending:
                        done, pending = wait(pending, return_when=FIRST_COMPLETED)
                        for future in done:
                            progress.advance(task)
                            if result := future.result():
                                kind, content = result
                                save_sample(kind, content)
                                os._exit(0)
                            if (s := next(seed_stream, None)) is not None:
                                pending.add(executor.submit(try_seed, s))
                except KeyboardInterrupt:
                    found.set()  # signal workers to stop early
                    progress.stop()
                    print("\nInterrupted.")
                    os._exit(1)
