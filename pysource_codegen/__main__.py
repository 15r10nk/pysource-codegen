import argparse

from ._codegen import generate


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, help="seed value")
    args = parser.parse_args()
    print(generate(args.seed))


if __name__ == "__main__":
    run()
