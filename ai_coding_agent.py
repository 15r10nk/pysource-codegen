import os
import subprocess
from pathlib import Path
from typing import Optional
from typing import Tuple

import logfire
from pydantic_ai import Agent
from pydantic_ai import UsageLimits
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.grok import GrokProvider


logfire.configure()
logfire.instrument_pydantic_ai()


# Global project root
project_root = Path(__file__).parent.resolve()


# Agent for code editing
def get_api_key() -> str:
    api_key = os.environ.get("XAI_API_KEY")
    if not api_key:
        raise RuntimeError("Environment variable XAI_API_KEY is not set.")
    return api_key


def to_path(path: str) -> Path:
    result = (project_root / path).resolve()
    if not str(result).startswith(str(project_root)):
        raise ValueError(f"Access denied: {path} is outside the project directory.")
    return result


agent = Agent(
    model=OpenAIChatModel(
        "grok-code-fast-1",
        provider=GrokProvider(api_key=get_api_key()),
    ),
    system_prompt="""
        You are a professional Python developer with deep knowledge of Python syntax and AST.
    """,
    instrument=True,
)


def run_tests_in_subprocess():
    return subprocess.run(
        ["uv", "run", "-p", "3.14.0", "-m", "unittest"],
        capture_output=True,
        check=False,
    )


@agent.tool_plain
async def run_tests() -> str:
    """
    Runs the test suite using uv and returns the combined output.
    """
    try:
        result = run_tests_in_subprocess()
        output = result.stdout + result.stderr
        return output.decode(errors="replace")
    except Exception as e:
        return f"Error running tests: {e}"


@agent.tool_plain
async def check_types() -> str:
    """
    check the types with mypy
    """
    try:
        result = subprocess.run("hatch run types:check".split(), capture_output=True)
        if result.returncode == 0:
            return "<there are no type errors>"

        output = result.stdout + result.stderr
        return output.decode(errors="replace")
    except Exception as e:
        return f"Error running tests: {e}"


@agent.tool_plain
async def read_code(filename: str, line_range: Optional[Tuple[int, int]] = None) -> str:
    """
    Reads the code of `filename`. A `line_range` can be provided to limit the output to the needed lines.
    You can only read files inside this project directory
    """
    file_path = to_path(filename)
    try:
        if line_range is not None:
            start, end = line_range
            with open(file_path, encoding="utf-8") as f:
                lines = f.readlines()
            return "".join(lines[start:end])
        else:
            return file_path.read_text(encoding="utf-8")
    except Exception as e:
        return f"Error reading file {filename}: {e}"


@agent.tool_plain
async def write_code(filename: str, text: str) -> str:
    """
    Write `text` into `filename`.
    You can only write to files inside pysource_codegen.
    """
    file_path = to_path(filename)
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(text, encoding="utf-8")
        return f"Successfully wrote to {filename}."
    except Exception as e:
        return f"Error writing to file {filename}: {e}"


@agent.tool_plain
async def list_files(directory: Optional[str] = None) -> list[str]:
    """
    List files in the given directory (relative to project root).
    You can only list files inside this project directory.
    """
    files = (
        subprocess.run(
            "git ls-files --others --exclude-standard --cached".split(),
            capture_output=True,
        )
        .stdout.decode()
        .splitlines()
    )
    files = [
        file
        for file in files
        if "samples/" not in file and file.startswith(directory or "")
    ]
    return files


if __name__ == "__main__":
    import asyncio

    async def main() -> None:

        if run_tests_in_subprocess().returncode != 0:
            result = await agent.run(
                "run the tests and explain the problems to me.",
                usage_limits=UsageLimits(response_tokens_limit=10000),
            )
            print(result.output)

    asyncio.run(main())
