import argparse
import os
import threading
from concurrent.futures import as_completed
from concurrent.futures import ThreadPoolExecutor
from random import randint

from tests.test_invalid_ast import generate_invalid_ast
from tests.test_valid_source import generate_valid_source

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, help="Test only one seed value")
    parser.add_argument(
        "--workers", type=int, default=os.cpu_count(), help="Number of parallel workers"
    )
    args = parser.parse_args()

    if args.seed is not None:
        print(f"Testing seed {args.seed}")
        if args.seed % 2 == 0:
            generate_invalid_ast(args.seed)
        else:
            generate_valid_source(args.seed)
    else:
        found = threading.Event()

        def try_seed():
            while not found.is_set():
                i = randint(0, 10000000000)
                if generate_invalid_ast(i) if i % 2 == 0 else generate_valid_source(i):
                    found.set()
                    return i

        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            futures = [executor.submit(try_seed) for _ in range(args.workers)]
            for future in as_completed(futures):
                result = future.result()
                if result is not None:
                    print(f"Found seed: {result}")
                    os._exit(0)
