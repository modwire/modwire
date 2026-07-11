from modwire import Modwire
from modwire.architecture import ArchitectureConfig
from modwire_extraction.code import CodeMap, QueryableCodeMap


def test_public_api_evaluates_each_configured_flow_realm() -> None:
    config = ArchitectureConfig(
        boundaries={
            "tags": (
                {"name": "backend_module", "match": "backend/*"},
                {"name": "gui_page", "match": "gui/pages/*"},
            ),
            "flow": {
                "realms": (
                    {"name": "backend", "module_tag": "backend_module"},
                    {"name": "gui", "module_tag": "gui_page"},
                ),
                "analyzers": ("no-cycles",),
            },
        }
    )
    code_map = queryable_map(
        "backend/orders/service.py",
        "backend/billing/service.py",
        "gui/pages/home.py",
        "gui/pages/settings.py",
        edges=(
            (
                "backend/orders/service.py",
                "backend/billing/service.py",
                "resolved",
                "billing.service",
            ),
            (
                "backend/billing/service.py",
                "backend/orders/service.py",
                "resolved",
                "orders.service",
            ),
            (
                "gui/pages/home.py",
                "gui/pages/settings.py",
                "resolved",
                "pages.settings",
            ),
            (
                "gui/pages/settings.py",
                "gui/pages/home.py",
                "resolved",
                "pages.home",
            ),
        ),
    )

    flow = report(code_map, config, "architecture.violations.flow")

    assert tuple(violation.rule_name for violation in flow.violations) == (
        "analyzer:backend:no-cycles",
        "analyzer:gui:no-cycles",
    )


def test_public_api_enforces_closed_module_boundaries() -> None:
    config = ArchitectureConfig(
        boundaries={
            "tags": (
                {"name": "module", "match": "src/*"},
                {"name": "shared", "match": "src/shared"},
            ),
            "rules": (
                {
                    "source": "module",
                    "disallow": ("module",),
                    "allow": ("shared",),
                    "allow_same_match": True,
                },
                {"source": "shared", "disallow": ("module",)},
            ),
            "flow": {"module_tag": "module"},
        }
    )
    code_map = queryable_map(
        "src/a/one.py",
        "src/a/two.py",
        "src/b/one.py",
        "src/shared/base.py",
        "tools.py",
        edges=(
            ("src/a/one.py", "src/a/two.py", "resolved", "a.two"),
            ("src/a/one.py", "src/shared/base.py", "resolved", "shared.base"),
            ("src/a/one.py", "src/b/one.py", "resolved", "b.one"),
            ("tools.py", "src/a/one.py", "resolved", "a.one"),
            ("src/a/one.py", None, "external", "json"),
            ("src/a/one.py", None, "unresolved", "missing"),
        ),
    )
    application = Modwire().architecture(config)

    first = application.report(code_map)
    second = application.report(code_map)
    flow = next(
        item for item in first if item.metadata.id == "architecture.violations.flow"
    )
    violations = tuple(
        violation
        for violation in flow.violations
        if violation.violation_type == "module-boundaries"
    )

    assert first == second
    assert tuple(violation.rule_name for violation in violations) == (
        "boundary:module",
        "boundary:unclassified",
    )
    forbidden = violations[0]
    assert forbidden.path == ("src/a/one.py", "src/b/one.py")
    assert forbidden.source_module == "module:a"
    assert forbidden.target_module == "module:b"
    assert forbidden.message == (
        "tracked cross-module dependency matches an explicit disallow"
    )
    assert violations[1].path == ("tools.py",)


def report(
    code_map: QueryableCodeMap,
    config: ArchitectureConfig,
    report_id: str,
):
    return next(
        item
        for item in Modwire().architecture(config).report(code_map)
        if item.metadata.id == report_id
    )


def queryable_map(
    *paths: str,
    edges: tuple[tuple[str, str | None, str, str], ...] = (),
) -> QueryableCodeMap:
    files = {path: source_file(path) for path in paths}
    code_map = CodeMap.from_dict(
        {
            "language": "test",
            "extraction": {
                "files": files,
                "modules": {
                    source["module_id"]: file_id
                    for file_id, source in files.items()
                },
                "files_found": len(files),
                "files_excluded": 0,
            },
            "dependency_graph": {
                "nodes": {
                    path: {"id": path, "kind": "file"}
                    for path in paths
                },
                "edges": [
                    {
                        "from_id": source,
                        "to_id": target,
                        "specifier": specifier,
                        "resolution": resolution,
                        "kind": "import",
                    }
                    for source, target, resolution, specifier in edges
                ],
            },
        }
    )
    return QueryableCodeMap(code_map=code_map)


def source_file(file_id: str) -> dict[str, object]:
    return {
        "file_id": file_id,
        "module_id": file_id.rsplit(".", 1)[0],
        "imports": [],
        "exports": [],
        "classes": [],
        "interfaces": [],
        "types": [],
        "abstract_classes": [],
        "functions": [],
        "values": [],
        "callables": [],
        "calls": [],
        "line_count": 1,
        "code_line_count": 1,
        "public_symbol_count": 0,
    }
