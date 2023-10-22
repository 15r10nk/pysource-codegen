def pytest_addoption(parser, pluginmanager):
    parser.addoption(
        "--generate-samples",
        action="store_true",
        help="Config file to use, defaults to %(default)s",
    )


def pytest_sessionfinish(session, exitstatus):
    print("exitstatus", exitstatus)

    if exitstatus == 0 and session.config.option.generate_samples:
        from .test_invalid_ast import generate_invalid_ast

        for i in range(20):
            generate_invalid_ast()
