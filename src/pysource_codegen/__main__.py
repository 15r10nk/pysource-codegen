import argparse

from ._codegen import generate


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, help="seed value")
    parser.add_argument(
        "--node-limit", type=int, default=400, help="limit number of nodes"
    )
    parser.add_argument(
        "--depth-limit", type=int, default=5, help="limit for the depth of the ast"
    )
    parser.add_argument("--root-node", type=str, default="Module", help="root ast type")
    args = parser.parse_args()

    print(
        generate(
            args.seed,
            node_limit=args.node_limit,
            depth_limit=args.depth_limit,
            root_node=args.root_node,
        )
    )


if __name__ == "__main__":
    run()
