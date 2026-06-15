from __future__ import annotations

from ..definitions import SourceFile, SourceImport
from ..extraction import CodeMap, ExtractionResult, ExtractionSummary
from ..graph import DependencyGraph


def source_import(
    path: str,
    *,
    normalized_path: str = "",
    imported_name: str = "",
    is_relative: bool = False,
    is_aliased: bool = False,
    crossing_type: str = "module",
    file_barrier_crossed: bool = True,
    statement_id: int = 1,
    join_key: str = "",
    uses_joined_import: bool = False,
) -> SourceImport:
    return SourceImport(
        path=path,
        is_relative=is_relative,
        normalized_path=normalized_path or path,
        imported_name=imported_name,
        is_aliased=is_aliased,
        crossing_type=crossing_type,
        file_barrier_crossed=file_barrier_crossed,
        statement_id=statement_id,
        join_key=join_key,
        uses_joined_import=uses_joined_import,
    )


def source_file(
    *,
    imports: tuple[SourceImport, ...] = (),
    line_count: int = 1,
    code_line_count: int = 1,
    public_symbol_count: int = 0,
) -> SourceFile:
    return SourceFile(
        imports=list(imports),
        exports=[],
        classes=[],
        interfaces=[],
        types=[],
        abstract_classes=[],
        functions=[],
        line_count=line_count,
        code_line_count=code_line_count,
        public_symbol_count=public_symbol_count,
    )


def dependency_graph(
    edges: tuple[tuple[str, str], ...] = (),
    nodes: tuple[str, ...] = (),
) -> DependencyGraph:
    graph = DependencyGraph()
    for node_id in nodes:
        graph.add_node(node_id)
    for source, target in edges:
        graph.add_edge(source, target)
    return graph


def code_map(
    files: tuple[str, ...] = (),
    edges: tuple[tuple[str, str], ...] = (),
    *,
    runtime_command: str = "python",
) -> CodeMap:
    graph = dependency_graph(edges, nodes=files)
    extraction_files = {
        source_id: source_file(
            imports=tuple(
                source_import(target)
                for source, target in edges
                if source == source_id
            )
        )
        for source_id in files
    }
    return CodeMap(
        graph=graph,
        extraction_result=ExtractionResult(
            files=extraction_files,
            summary=ExtractionSummary(
                files_found=len(files),
                files_checked=len(files),
                files_excluded=0,
            ),
        ),
        runtime_command=runtime_command,
    )
