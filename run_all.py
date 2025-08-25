# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "rich",
# ]
# ///
import json
import re
import subprocess

from rich.console import Console
from rich.table import Table


def parse_version(s):
    """
    Returns (major, minor, patch, pre_type, pre_num)
    pre_type: None, 'a', or 'rc'
    pre_num: int or None
    """
    m = re.match(r"(\d+)\.(\d+)\.(\d+)(?:(a|rc)(\d+))?", s)
    if not m:
        raise ValueError(f"Invalid version string: {s}")
    major, minor, patch = map(int, m.group(1, 2, 3))
    pre_type = m.group(4)
    pre_num = int(m.group(5)) if m.group(5) else None
    return (major, minor, patch, pre_type, pre_num)


def version_tuple(s):
    # Remove rc or alpha suffixes if present for stable comparison
    v = parse_version(s)
    return (v[0], v[1], v[2])


def pre_release_key(s):
    v = parse_version(s)
    # None < a < rc, and lower numbers first
    if v[3] is None:
        return (0, 0)  # stable
    elif v[3] == "a":
        return (1, v[4] or 0)
    elif v[3] == "rc":
        return (2, v[4] or 0)
    else:
        return (3, 0)  # unknown, sort last


result = subprocess.run(
    ["uv", "python", "list", "--all-versions", "--output-format=json"],
    capture_output=True,
)

versions = set()
for e in json.loads(result.stdout):
    if e["implementation"] != "cpython":
        continue
    versions.add(e["version"])

# Group versions by minor version and type
stable = {}
pre = {}

for v in versions:
    vt = version_tuple(v)
    minor = f"{vt[0]}.{vt[1]}"
    pv = parse_version(v)
    if pv[3] is not None:
        # pre-release: keep only the most recent per minor
        if minor not in pre or pre_release_key(v) > pre_release_key(pre[minor]):
            pre[minor] = v
    else:
        stable.setdefault(minor, []).append(v)

# Collect all stable versions and the most recent pre-release per minor
filtered_versions = []
for minor in stable:
    filtered_versions.extend(stable[minor])
for minor in pre:
    filtered_versions.append(pre[minor])

versions = sorted(
    [v for v in filtered_versions if version_tuple(v) >= (3, 8)], key=version_tuple
)

results = {}


for version in versions:
    result = subprocess.run(
        ["uvx", "-p", version, "--with-editable=.", "python", "-m", "unittest", "-v"],
        capture_output=True,
        text=True,
    )
    for line in result.stderr.splitlines():
        if line.startswith("FAIL: "):
            # Example line: FAIL: test_func (module.Class)
            fail_info = line.split()
            test_func = fail_info[1]
            module_class = fail_info[2].strip("()")
            if not module_class.endswith(test_func):
                module_class += "." + test_func

            print(f"uvx -p {version} python -m unittest {module_class}")
    results[version] = result.returncode


# results={'3.9.10': 0, '3.11.3': 0, '3.13.4': 0, '3.10.17': 0, '3.11.8': 0, '3.10.16': 0, '3.12.4': 1, '3.8.11': 0, '3.10.0': 0, '3.9.22': 0, '3.12.2': 1, '3.13.3': 0, '3.8.9': 0, '3.11.11': 0, '3.10.15': 0, '3.9.4': 0, '3.8.14': 0, '3.8.20': 0, '3.12.7': 1, '3.9.12': 0, '3.9.16': 0, '3.11.13': 0, '3.9.7': 0, '3.9.15': 0, '3.12.5': 1, '3.12.11': 1, '3.8.19': 0, '3.10.14': 0, '3.10.4': 0, '3.9.5': 0, '3.9.21': 0, '3.9.0': 1, '3.11.1': 0, '3.10.9': 0, '3.9.17': 0, '3.12.6': 1, '3.10.2': 0, '3.11.4': 0, '3.13.0': 0, '3.12.1': 1, '3.11.12': 0, '3.10.8': 0, '3.8.3': 0, '3.9.6': 0, '3.9.18': 0, '3.10.13': 0, '3.8.15': 0, '3.9.13': 0, '3.11.6': 0, '3.8.12': 0, '3.11.2': 0, '3.13.1': 0, '3.8.13': 0, '3.8.2': 0, '3.8.18': 0, '3.9.11': 0, '3.12.3': 1, '3.8.5': 0, '3.8.10': 0, '3.12.8': 1, '3.13.2': 0, '3.8.16': 0, '3.10.11': 0, '3.7.9': 1, '3.9.1': 1, '3.8.17': 0, '3.10.6': 0, '3.13.6': 0, '3.10.5': 0, '3.10.7': 0, '3.11.9': 0, '3.9.19': 0, '3.12.10': 1, '3.8.8': 0, '3.13.5': 0, '3.9.20': 0, '3.9.14': 0, '3.12.9': 1, '3.8.7': 0, '3.12.0': 1, '3.8.6': 0, '3.10.18': 0, '3.11.7': 0, '3.11.5': 0, '3.10.12': 0, '3.9.3': 0, '3.10.3': 0, '3.11.10': 0, '3.9.23': 0, '3.9.2': 1}

# Group results by minor version
minor_versions = {}
for version, returncode in results.items():
    minor = ".".join(version.split(".")[:2])
    minor_versions.setdefault(minor, []).append((version, returncode))

# Sort minor versions and versions within each minor
sorted_minor_versions = sorted(
    minor_versions.keys(), key=lambda v: tuple(map(int, v.split(".")))
)
for minor in sorted_minor_versions:
    minor_versions[minor].sort(key=lambda x: version_tuple(x[0]))

# Prepare table
table = Table(title="Python Test Results by Minor Version")
for minor in sorted_minor_versions:
    table.add_column(minor, justify="left")

# Find max number of patch versions in any minor version
max_rows = max(len(v) for v in minor_versions.values())

# Fill table rows
for i in range(max_rows):
    row = []
    for minor in sorted_minor_versions:
        if i < len(minor_versions[minor]):
            version, returncode = minor_versions[minor][i]
            status = "[green]ok[/green]" if returncode == 0 else "[red]failed[/red]"
            row.append(f"{version} {status}")
        else:
            row.append("")
    table.add_row(*row)

console = Console()
console.print(table)
