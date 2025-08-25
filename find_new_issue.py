import argparse
import os
import threading
from concurrent.futures import as_completed
from concurrent.futures import ThreadPoolExecutor
from random import randint

from tests.test_invalid_ast import generate_invalid_ast

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, help="Test only one seed value")
    parser.add_argument(
        "--workers", type=int, default=os.cpu_count(), help="Number of parallel workers"
    )
    args = parser.parse_args()

    if args.seed is not None:
        print(f"Testing seed {args.seed}")
        generate_invalid_ast(args.seed)
    else:
        found = threading.Event()

        def try_seed():
            while not found.is_set():
                i = randint(0, 10000000000)
                if generate_invalid_ast(i):
                    found.set()
                    print(f"Found seed: {i}")
                    return i

        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            futures = [executor.submit(try_seed) for _ in range(args.workers)]
            for future in as_completed(futures):
                if future.result() is not None:
                    break
