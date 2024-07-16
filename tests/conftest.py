import random
import time
from multiprocessing import get_context

from .test_invalid_ast import generate_invalid_ast


def pytest_addoption(parser, pluginmanager):
    parser.addoption(
        "--generate-samples",
        action="store_true",
        help="Config file to use, defaults to %(default)s",
    )


def generate(seed):
    return generate_invalid_ast(seed)  # or generate_valid_source(seed)


def seeds():
    return [random.randint(0, 10000000) for _ in range(10000)]


def pytest_sessionfinish(session, exitstatus):
    print("exitstatus", exitstatus)

    if exitstatus == 0 and session.config.option.generate_samples:
        end_time = time.time() + 60 * 5
        if False:
            for seed in seeds():
                if generate(seed):
                    break
                if time.time() > end_time:
                    print("Timeout")
                    break
        else:
            with get_context("spawn").Pool(maxtasksperchild=100) as p:
                for r in p.imap_unordered(generate, seeds()):
                    if r:
                        break

                    if time.time() > end_time:
                        print("Timeout")
                        break
                p.terminate()
