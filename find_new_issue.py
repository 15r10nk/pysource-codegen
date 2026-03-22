import argparse
import hashlib
import itertools
import os
import subprocess
import threading
from concurrent.futures import as_completed
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from random import randrange

from tests.test_invalid_ast import generate_invalid_ast
from tests.test_valid_source import generate_valid_source

if __name__ == "__main__":
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

    found = threading.Event()

    generators = {
        "invalid_ast": generate_invalid_ast,
        "valid_source": generate_valid_source,
    }
    kinds = sorted(generators)

    def save_sample(kind: str, content: str) -> None:
        sample_dir = Path(__file__).parent / "tests" / f"{kind}_samples"
        name = sample_dir / f"{hashlib.sha256(content.encode()).hexdigest()}.py"
        name.write_text(content)
        subprocess.run(["git", "add", str(name)], check=True)
        print(f"Saved: {name}")

    def try_seed(i: int) -> tuple[str, str] | None:
        if found.is_set():
            return None
        kind = kinds[i % len(kinds)]
        result = generators[kind](i)
        if (
            result and result is not True
        ):  # True = early-exit (generation bug), no sample
            found.set()
            return (kind, result)
        return None

    if args.seed is not None:
        print(f"Testing seed {args.seed}")
        result = try_seed(args.seed)
        if result:
            kind, content = result
            save_sample(kind, content)
    else:

        def random_seeds():
            while True:
                yield randrange(10_000_000_000)

        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            seed_stream = itertools.islice(random_seeds(), args.num_seeds)
            futures = {
                executor.submit(try_seed, s)
                for s in itertools.islice(seed_stream, args.workers)
            }
            try:
                for future in as_completed(futures):
                    if result := future.result():
                        kind, content = result
                        save_sample(kind, content)
                        os._exit(0)
                    if (s := next(seed_stream, None)) is not None:
                        futures.add(executor.submit(try_seed, s))
            except KeyboardInterrupt:
                found.set()  # signal workers to stop early
                print("\nInterrupted.")
                os._exit(1)
