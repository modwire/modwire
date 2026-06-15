from __future__ import annotations

from ..definitions import (
    SourceAbstractClass,
    SourceCall,
    SourceCallable,
    SourceClass,
    SourceClassMethod,
    SourceClassProperty,
    SourceFile,
    SourceFunction,
    SourceImport,
    SourceParameter,
    SourceValue,
)
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
    classes: tuple[SourceClass, ...] = (),
    abstract_classes: tuple[SourceAbstractClass, ...] = (),
    functions: tuple[SourceFunction, ...] = (),
    values: tuple[SourceValue, ...] = (),
    callables: tuple[SourceCallable, ...] = (),
    calls: tuple[SourceCall, ...] = (),
    line_count: int = 1,
    code_line_count: int = 1,
    public_symbol_count: int = 0,
) -> SourceFile:
    return SourceFile(
        imports=list(imports),
        exports=[],
        classes=list(classes),
        interfaces=[],
        types=[],
        abstract_classes=list(abstract_classes),
        functions=list(functions),
        values=list(values),
        callables=list(callables),
        calls=list(calls),
        line_count=line_count,
        code_line_count=code_line_count,
        public_symbol_count=public_symbol_count,
    )


def source_function(
    name: str,
    *,
    line_count: int = 1,
    declared_args: int = 0,
    optional_args: int = 0,
    visibility: str = "public",
    visibility_intent: str = "public",
) -> SourceFunction:
    return SourceFunction(
        name=name,
        visibility=visibility,
        visibility_intent=visibility_intent,
        line_count=line_count,
        declared_args=declared_args,
        optional_args=optional_args,
    )


def source_value(
    name: str,
    *,
    line_count: int = 1,
    declaration_kind: str = "assignment",
    value_kind: str = "unknown",
    declared_args: int = 0,
    optional_args: int = 0,
    visibility: str = "public",
    visibility_intent: str = "public",
) -> SourceValue:
    return SourceValue(
        name=name,
        visibility=visibility,
        visibility_intent=visibility_intent,
        line_count=line_count,
        declaration_kind=declaration_kind,
        value_kind=value_kind,
        declared_args=declared_args,
        optional_args=optional_args,
    )


def source_parameter(
    name: str,
    *,
    annotation: str = "",
    kind: str = "positional",
    has_default: bool = False,
) -> SourceParameter:
    return SourceParameter(
        name=name,
        annotation=annotation,
        kind=kind,
        has_default=has_default,
    )


def source_callable(
    callable_id: str,
    *,
    source_id: str = "app",
    name: str = "run",
    qualified_name: str = "",
    owner_name: str = "",
    kind: str = "function",
    line_start: int = 1,
    line_end: int = 1,
    parameters: tuple[SourceParameter, ...] = (),
    declared_args: int = 0,
    optional_args: int = 0,
    return_annotation: str = "",
    decorators: tuple[str, ...] = (),
    docstring: str = "",
    visibility: str = "public",
    visibility_intent: str = "public",
) -> SourceCallable:
    return SourceCallable(
        id=callable_id,
        source_id=source_id,
        name=name,
        qualified_name=qualified_name or name,
        owner_name=owner_name,
        kind=kind,
        visibility=visibility,
        visibility_intent=visibility_intent,
        line_start=line_start,
        line_end=line_end,
        line_count=line_end - line_start + 1,
        parameters=list(parameters),
        declared_args=declared_args,
        optional_args=optional_args,
        return_annotation=return_annotation,
        decorators=list(decorators),
        docstring=docstring,
    )


def source_call(
    source_callable_id: str,
    *,
    source_id: str = "app",
    line: int = 1,
    expression: str = "run",
    target_name: str = "run",
    target_callable_id: str = "",
    resolution: str = "unresolved",
) -> SourceCall:
    return SourceCall(
        source_callable_id=source_callable_id,
        target_callable_id=target_callable_id,
        source_id=source_id,
        line=line,
        expression=expression,
        resolution=resolution,
        target_name=target_name,
    )


def source_method(
    name: str,
    *,
    line_count: int = 1,
    declared_args: int = 0,
    optional_args: int = 0,
    visibility: str = "public",
    visibility_intent: str = "public",
) -> SourceClassMethod:
    return SourceClassMethod(
        name=name,
        visibility=visibility,
        visibility_intent=visibility_intent,
        line_count=line_count,
        declared_args=declared_args,
        optional_args=optional_args,
    )


def source_property(name: str, *, is_optional: bool = False) -> SourceClassProperty:
    return SourceClassProperty(name=name, is_optional=is_optional)


def source_class(
    name: str,
    *,
    methods: tuple[SourceClassMethod, ...] = (),
    properties: tuple[SourceClassProperty, ...] = (),
    line_count: int = 1,
    visibility: str = "public",
    visibility_intent: str = "public",
) -> SourceClass:
    return SourceClass(
        name=name,
        visibility=visibility,
        visibility_intent=visibility_intent,
        methods=list(methods),
        properties=list(properties),
        line_count=line_count,
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
