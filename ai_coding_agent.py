import os
import subprocess
from pathlib import Path
from typing import Optional
from typing import Tuple

import logfire
from pydantic_ai import Agent
from pydantic_ai import RunContext
from pydantic_ai import UsageLimits
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.grok import GrokProvider


logfire.configure()
logfire.instrument_pydantic_ai()


# Agent for code editing
def get_api_key() -> str:
    api_key = os.environ.get("XAI_API_KEY")
    if not api_key:
        raise RuntimeError("Environment variable XAI_API_KEY is not set.")
    return api_key


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


@agent.tool
async def run_tests(ctx: RunContext) -> str:
    """
    Runs the test suite using uv and returns the combined output.
    """
    try:
        result = subprocess.run(
            ["uv", "run", "-p", "3.14.0", "-m", "unittest"],
            capture_output=True,
            check=False,
        )
        output = result.stdout + result.stderr
        return output.decode(errors="replace")
    except Exception as e:
        return f"Error running tests: {e}"


@agent.tool
async def read_code(
    ctx: RunContext, filename: str, line_range: Optional[Tuple[int, int]] = None
) -> str:
    """
    Reads the code of `filename`. A `line_range` can be provided to limit the output to the needed lines.
    You can only read files inside this project directory
    """
    project_root = Path(__file__).parent.resolve()
    file_path = (
        (project_root / filename).resolve()
        if not os.path.isabs(filename)
        else Path(filename).resolve()
    )
    try:
        # Ensure file is inside project directory
        if not str(file_path).startswith(str(project_root)):
            return f"Access denied: {filename} is outside the project directory."
        if line_range is not None:
            start, end = line_range
            with open(file_path, encoding="utf-8") as f:
                lines = f.readlines()
            return "".join(lines[start:end])
        else:
            return file_path.read_text(encoding="utf-8")
    except Exception as e:
        return f"Error reading file {filename}: {e}"


@agent.tool
async def write_code(ctx: RunContext, filename: str, text: str) -> str:
    """
    Write `text` into `filename`.
    You can only write to files inside pysource_codegen.
    """
    project_root = Path(__file__).parent.resolve()
    file_path = (project_root / filename).resolve()
    try:
        # Ensure file is inside pysource_codegen
        if not str(file_path).startswith(str(project_root / "pysource_codegen")):
            return f"Access denied: {filename} is outside pysource_codegen."
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(text, encoding="utf-8")
        return f"Successfully wrote to {filename}."
    except Exception as e:
        return f"Error writing to file {filename}: {e}"


@agent.tool
async def list_files(ctx: RunContext, directory: Optional[str] = None) -> list[str]:
    """
    List files in the given directory (relative to project root).
    You can only list files inside this project directory.
    """
    project_root = Path(__file__).parent.resolve()
    dir_path = (project_root / directory).resolve() if directory else project_root
    try:
        # Ensure directory is inside project root
        if not str(dir_path).startswith(str(project_root)):
            return [f"Access denied: {dir_path} is outside the project directory."]
        return [
            str(p.relative_to(project_root)) for p in dir_path.rglob("*") if p.is_file()
        ]
    except Exception as e:
        return [f"Error listing files in {dir_path}: {e}"]


if __name__ == "__main__":
    import asyncio

    async def main() -> None:
        result = await agent.run(
            "run the tests and explain the problems to me.",
            usage_limits=UsageLimits(response_tokens_limit=100_000),
        )
        print(result.output)

    asyncio.run(main())
