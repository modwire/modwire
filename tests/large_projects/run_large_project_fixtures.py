from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = Path(__file__).with_name("fixtures.json")
DEFAULT_WORKSPACE = ROOT / ".dev" / "large-projects"
LOCAL_SOURCE = ROOT / "src"
OUTPUT_TAIL_LINES = 120
DEFAULT_COMMAND_TIMEOUT_SECONDS = 60
FILE_EXTENSIONS = {
    "python": (".py",),
    "typescript": (".ts", ".tsx", ".js", ".jsx"),
    "php": (".php",),
}

STRICT_MODWIRE_SHAPE_CONFIG = {
    "max_classes_per_file": 0,
    "max_interfaces_per_file": 0,
    "max_types_per_file": 0,
    "max_abstract_classes_per_file": 0,
    "max_functions_per_file": 0,
    "max_methods_per_class": 0,
    "max_declared_args": 0,
    "max_function_lines": 0,
    "max_method_lines": 0,
    "max_class_lines": 0,
    "allow_optional_function_args": False,
    "allow_optional_method_args": False,
    "allow_optional_class_properties": False,
    "allow_import_aliases": False,
    "allowed_import_crossing_types": (),
    "require_joined_imports": True,
}

STRICT_ENCLOSURE_SHAPE_CONFIG = {
    "max_classes_per_file": 0,
    "max_interfaces_per_file": 0,
    "max_types_per_file": 0,
    "max_abstract_classes_per_file": 0,
    "max_functions_per_file": 0,
    "max_methods_per_class": 0,
    "max_declared_args_per_function": 0,
    "max_declared_args_per_method": 0,
    "max_lines_count_per_function": 0,
    "max_lines_count_per_method": 0,
    "max_lines_count_per_class": 0,
    "allow_optional_function_args": False,
    "allow_optional_method_args": False,
    "allow_optional_class_properties": False,
    "allow_imports_aliases": False,
    "enforce_joined_imports": True,
    "allowed_imports_crossing_types": [],
}


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    manifest = load_manifest()
    fixtures = select_fixtures(
        manifest["fixtures"],
        tuple(args.fixture or ()),
        args.language,
    )
    if args.list:
        for fixture in fixtures:
            print(
                f"{fixture['id']}\t{fixture['language']}\t"
                f"{fixture['repository']}@{fixture['ref']}"
            )
        return 0

    summaries = []
    failures: list[tuple[str, str]] = []
    for fixture in fixtures:
        try:
            checkout = prepare_fixture(fixture, args.workspace)
            write_enclosure_config(fixture, checkout)
            if args.prepare_only:
                continue
            if args.mode in {"enclosure", "both"}:
                run_enclosure_suite(
                    checkout,
                    args.enclosure_command,
                    timeout_seconds=args.command_timeout,
                )
            if args.mode in {"modwire", "both"}:
                summary = run_modwire_stress(fixture, checkout)
                summaries.append(summary)
                print(json.dumps(summary, sort_keys=True))
        except Exception as exc:
            if not args.keep_going:
                raise
            failures.append((fixture["id"], str(exc)))
            print(f"Fixture failed: {fixture['id']}: {exc}", file=sys.stderr)

    if summaries:
        print(
            json.dumps(
                {
                    "fixtures": len(summaries),
                    "files_checked": sum(
                        summary["files_checked"] for summary in summaries
                    ),
                    "shape_violations": sum(
                        summary["shape_violations"] for summary in summaries
                    ),
                    "architecture_violations": sum(
                        summary["architecture_violations"] for summary in summaries
                    ),
                },
                sort_keys=True,
            )
        )
    if failures:
        print("Fixture failures:", file=sys.stderr)
        for fixture_id, message in failures:
            print(f"- {fixture_id}: {message}", file=sys.stderr)
        return 1
    return 0


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepare and run pinned large-project extraction fixtures."
    )
    parser.add_argument(
        "--workspace",
        type=Path,
        default=DEFAULT_WORKSPACE,
        help="Directory used for cloned large-project fixtures.",
    )
    parser.add_argument(
        "--fixture",
        action="append",
        help="Fixture id to run. Can be passed multiple times.",
    )
    parser.add_argument(
        "--language",
        choices=("python", "typescript", "php"),
        help="Run every fixture for one supported language.",
    )
    parser.add_argument(
        "--prepare-only",
        action="store_true",
        help="Clone and configure fixtures without running extraction.",
    )
    parser.add_argument(
        "--mode",
        choices=("enclosure", "modwire", "both"),
        default="enclosure",
        help="Run the e2e enclosure CLI suite, direct modwire stress checks, or both.",
    )
    parser.add_argument(
        "--enclosure-command",
        default="enclosure",
        help="Enclosure executable to run for e2e checks.",
    )
    parser.add_argument(
        "--command-timeout",
        type=int,
        default=DEFAULT_COMMAND_TIMEOUT_SECONDS,
        help=(
            "Seconds allowed for each enclosure command. Defaults to a fail-fast "
            "ceiling so broken fixtures do not stall local or CI runs."
        ),
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List selected fixtures without cloning or running them.",
    )
    parser.add_argument(
        "--keep-going",
        action="store_true",
        help="Run remaining selected fixtures after a fixture fails.",
    )
    return parser.parse_args(argv)


def load_manifest() -> dict[str, Any]:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def select_fixtures(
    fixtures: list[dict[str, Any]],
    fixture_ids: tuple[str, ...],
    language: str | None,
) -> list[dict[str, Any]]:
    selected = fixtures
    if fixture_ids:
        wanted = set(fixture_ids)
        selected = [fixture for fixture in selected if fixture["id"] in wanted]
        missing = wanted.difference(fixture["id"] for fixture in selected)
        if missing:
            raise SystemExit(f"Unknown fixture id: {', '.join(sorted(missing))}")
    if language is not None:
        selected = [fixture for fixture in selected if fixture["language"] == language]
    return selected


def prepare_fixture(fixture: dict[str, Any], workspace: Path) -> Path:
    checkout = workspace / fixture["id"]
    workspace.mkdir(parents=True, exist_ok=True)
    if not checkout.joinpath(".git").is_dir():
        run(
            [
                "git",
                "clone",
                "--filter=blob:none",
                "--no-checkout",
                fixture["repository"],
                str(checkout),
            ],
            cwd=workspace,
        )
    ensure_origin(checkout, fixture["repository"])
    if current_head(checkout) == fixture["ref"] and has_language_files(checkout, fixture):
        return checkout
    run(["git", "-C", str(checkout), "fetch", "--depth", "1", "origin", fixture["ref"]])
    run(["git", "-C", str(checkout), "checkout", "--force", fixture["ref"]])
    return checkout


def current_head(checkout: Path) -> str:
    result = subprocess.run(
        ["git", "-C", str(checkout), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=False,
        env=local_env(),
    )
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def ensure_origin(checkout: Path, repository: str) -> None:
    result = subprocess.run(
        ["git", "-C", str(checkout), "remote", "get-url", "origin"],
        capture_output=True,
        text=True,
        check=False,
        env=local_env(),
    )
    if result.returncode == 0:
        if result.stdout.strip() != repository:
            run(["git", "-C", str(checkout), "remote", "set-url", "origin", repository])
        return
    run(["git", "-C", str(checkout), "remote", "add", "origin", repository])


def has_language_files(checkout: Path, fixture: dict[str, Any]) -> bool:
    source_root = checkout / fixture["source_root"]
    extensions = FILE_EXTENSIONS[fixture["language"]]
    ignored_dirs = {".git", ".enclosure"}
    for root, dirs, files in os.walk(source_root):
        dirs[:] = [directory for directory in dirs if directory not in ignored_dirs]
        if any(file.endswith(extensions) for file in files):
            return True
    return False


def write_enclosure_config(fixture: dict[str, Any], checkout: Path) -> None:
    config_dir = checkout / ".enclosure"
    config_dir.mkdir(parents=True, exist_ok=True)
    config_dir.joinpath("rules", "local").mkdir(parents=True, exist_ok=True)
    config_dir.joinpath("rules", "shared").mkdir(parents=True, exist_ok=True)
    config_dir.joinpath("recipes").mkdir(parents=True, exist_ok=True)
    config_dir.joinpath("enclosure.yaml").write_text(
        render_enclosure_yaml(fixture),
        encoding="utf-8",
    )


def run_modwire_stress(fixture: dict[str, Any], checkout: Path) -> dict[str, Any]:
    from modwire import evaluate_shape, extract_code
    from modwire.architecture import ArchitecturePolicyEvaluator

    source_root = checkout / fixture["source_root"]
    code_map = extract_code(
        fixture["language"],
        source_root,
        tuple(fixture["exclusions"]),
    )
    if code_map.extraction_result.summary.files_checked == 0:
        raise RuntimeError(f"{fixture['id']} extracted zero files")

    shape_violations = evaluate_shape(code_map, STRICT_MODWIRE_SHAPE_CONFIG)
    architecture_violations = ArchitecturePolicyEvaluator().evaluate(
        code_map.graph,
        architecture_config(fixture),
    )
    return {
        "fixture": fixture["id"],
        "language": fixture["language"],
        "ref": fixture["ref"],
        "files_found": code_map.extraction_result.summary.files_found,
        "files_checked": code_map.extraction_result.summary.files_checked,
        "files_excluded": code_map.extraction_result.summary.files_excluded,
        "edges": len(code_map.graph.edges),
        "shape_violations": len(shape_violations),
        "architecture_violations": len(architecture_violations),
    }


def run_enclosure_suite(
    checkout: Path,
    enclosure_command: str,
    *,
    timeout_seconds: int,
) -> None:
    if shutil.which(enclosure_command) is None:
        raise RuntimeError(f"`{enclosure_command}` command is not available")
    commands = (
        ([enclosure_command, "architecture", "map"], (0,)),
        ([enclosure_command, "architecture", "boundaries"], (0, 1)),
        ([enclosure_command, "health"], (0, 1)),
        ([enclosure_command, "architecture", "shape"], (0, 1)),
        ([enclosure_command, "architecture", "health", "--vv"], (0, 1)),
        ([enclosure_command, "architecture", "pressure", "--top", "20"], (0,)),
        ([enclosure_command, "architecture", "clusters", "--top", "20"], (0,)),
        ([enclosure_command, "architecture", "coherence", "--top", "20"], (0,)),
    )
    for command, accepted_exit_codes in commands:
        run(
            command,
            cwd=checkout,
            accepted_exit_codes=accepted_exit_codes,
            timeout_seconds=timeout_seconds,
        )


def architecture_config(fixture: dict[str, Any]) -> dict[str, Any]:
    return {
        "language": fixture["language"],
        "architecture_root": "",
        "rules": {
            "tags": fixture["tags"],
            "boundaries": boundary_rules(fixture["layers"]),
            "flow": {
                "layers": fixture["layers"],
                "module_tag": fixture["module_tag"],
                "analyzers": ("backward-flow", "no-reentry", "no-cycles"),
            },
        },
    }


def boundary_rules(layers: list[str]) -> list[dict[str, Any]]:
    return [
        {
            "source": layer,
            "disallow": layers[:index],
            "allow": [],
            "allow_same_match": True,
        }
        for index, layer in enumerate(layers)
        if index > 0
    ]


def render_enclosure_yaml(fixture: dict[str, Any]) -> str:
    lines = [
        "architecture:",
        f"  language: {yaml_scalar(fixture['language'])}",
        f"  root: {yaml_scalar(fixture['source_root'])}",
        "  exclusions:",
    ]
    lines.extend(f"    - {yaml_scalar(pattern)}" for pattern in fixture["exclusions"])
    lines.append("  shape:")
    for key, value in STRICT_ENCLOSURE_SHAPE_CONFIG.items():
        lines.append(f"    {key}: {yaml_scalar(value)}")
    lines.extend(
        [
            "  boundaries:",
            "    tags:",
        ]
    )
    for tag in fixture["tags"]:
        lines.extend(
            [
                f"      - name: {yaml_scalar(tag['name'])}",
                f"        match: {yaml_scalar(tag['match'])}",
                "        except: []",
                "        exclude: []",
            ]
        )
    lines.append("    rules:")
    for rule in boundary_rules(fixture["layers"]):
        lines.extend(
            [
                f"      - source: {yaml_scalar(rule['source'])}",
                "        disallow:",
            ]
        )
        lines.extend(
            f"          - {yaml_scalar(layer)}" for layer in rule["disallow"]
        )
        lines.extend(
            [
                "        allow: []",
                "        allow_same_match: true",
            ]
        )
    lines.extend(
        [
            "    flow:",
            "      layers:",
        ]
    )
    lines.extend(f"        - {yaml_scalar(layer)}" for layer in fixture["layers"])
    lines.extend(
        [
            f"      module_tag: {yaml_scalar(fixture['module_tag'])}",
            "      analyzers:",
            "        - backward-flow",
            "        - no-reentry",
            "        - no-cycles",
            "  map:",
            "    top: 20",
            "  pressure:",
            "    top: 20",
            "  clusters:",
            "    group_depth: 5",
            "    top: 20",
            "    files_top: 5",
            "  health:",
            "    top: 20",
            "",
            "workspace:",
            "  recipe:",
            "    skip:",
            "      - \"**/__pycache__/**\"",
            "      - \"__pycache__/**\"",
            "    roles_map:",
            "      architecture/boundaries: module-report-cli",
            "      architecture/clusters: module-report-cli",
            "      architecture/coherence: module-domain-package-cli",
            "      architecture/config: module-config-support",
            "      architecture/health: module-report-cli",
            "      architecture/map: module-report-cli",
            "      architecture/pressure: module-report-cli",
            "      architecture/shape: module-report-cli",
            "      health/report: module-report-cli",
            "      workspace/config: module-config-support",
            "      workspace/health: module-report-cli",
            "      workspace/plan: module-workspace-cli",
            "      workspace/recipe: module-workspace-cli",
            "      workspace/rules: module-domain-package-cli",
            "      workspace/sync: module-workspace-cli",
            "  rules:",
            "    local:",
            "      max_content_chars: 2400",
            "  sync: {}",
        ]
    )
    return "\n".join(lines) + "\n"


def yaml_scalar(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, list | tuple):
        if not value:
            return "[]"
        return "[" + ", ".join(yaml_scalar(item) for item in value) + "]"
    if isinstance(value, int):
        return str(value)
    return json.dumps(value)


def run(
    command: list[str],
    *,
    cwd: Path | None = None,
    accepted_exit_codes: tuple[int, ...] = (0,),
    timeout_seconds: int | None = None,
) -> None:
    print("+ " + " ".join(command), flush=True)
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            check=False,
            env=local_env(),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired as exc:
        output = exc.stdout or ""
        if isinstance(output, bytes):
            output = output.decode("utf-8", errors="replace")
        print_output_tail(output, lines=OUTPUT_TAIL_LINES)
        raise
    has_cli_error = any(
        line.startswith("Error:") for line in result.stdout.splitlines()
    )
    if result.returncode not in accepted_exit_codes or has_cli_error:
        print_output_tail(result.stdout, lines=OUTPUT_TAIL_LINES)
        raise subprocess.CalledProcessError(result.returncode, command)
    print_output_tail(result.stdout, lines=OUTPUT_TAIL_LINES)


def local_env() -> dict[str, str]:
    env = dict(os.environ)
    pythonpath = env.get("PYTHONPATH", "")
    paths = [str(LOCAL_SOURCE), *(path for path in pythonpath.split(":") if path)]
    env["PYTHONPATH"] = ":".join(paths)
    return env


def print_output_tail(output: str, *, lines: int) -> None:
    if not output:
        return
    output_lines = output.splitlines()
    if len(output_lines) > lines:
        print(f"... output truncated to last {lines} lines ...")
        output_lines = output_lines[-lines:]
    print("\n".join(output_lines))


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
