from pathlib import Path

import nox
from nox_poetry import session

nox.options.sessions = ["clean", "test", "report", "mypy"]
nox.options.reuse_existing_virtualenvs = True

python_versions = ["3.7", "3.8", "3.9", "3.10", "3.11"]


@session(python="python3.11")
def clean(session):
    session.install("coverage")
    session.env["TOP"] = str(Path(__file__).parent)
    session.run("coverage", "erase")


@session(python=python_versions)
def mypy(session):
    session.install(".", "mypy", "pytest", "rich")
    session.run("mypy", "pysource_codegen", "tests")


@session(python=python_versions)
def test(session):
    session.install(".", "pytest", "pytest-xdist", "rich", "coverage-enable-subprocess")
    session.env["COVERAGE_PROCESS_START"] = str(
        Path(__file__).parent / "pyproject.toml"
    )
    session.env["TOP"] = str(Path(__file__).parent)
    args = [] if session.posargs else ["-n", "auto", "-v"]

    session.run(
        "pytest", "-W", "ignore::SyntaxWarning", *args, "tests", *session.posargs
    )


@session(python="python3.11")
def report(session):
    session.install("coverage")

    session.env["TOP"] = str(Path(__file__).parent)
    try:
        session.run("coverage", "combine")
    except:
        pass
    session.run("coverage", "html")
    session.run("coverage", "report")
