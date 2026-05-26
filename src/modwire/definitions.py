from typing import Literal

from pydantic import BaseModel, Field


ImportCrossingType = Literal["module", "symbol"]
SourceVisibility = Literal["public", "protected", "private"]
SourceSignatureKind = Literal["call", "construct", "index"]
SourceExportKind = Literal[
    "module",
    "class",
    "interface",
    "type",
    "abstract_class",
    "function",
    "value",
    "unknown",
]


class SourceImportedSymbol(BaseModel):
    name: str
    alias: str
    is_aliased: bool
    is_default: bool
    is_namespace: bool
    is_star: bool


class SourceImport(BaseModel):
    path: str
    is_relative: bool
    normalized_path: str
    imported_name: str
    is_aliased: bool
    crossing_type: ImportCrossingType
    file_barrier_crossed: bool
    statement_id: int
    join_key: str
    uses_joined_import: bool
    imported_symbols: list[SourceImportedSymbol] = Field(default_factory=list)


class SourceExport(BaseModel):
    name: str
    local_name: str
    kind: SourceExportKind
    crossing_type: ImportCrossingType
    path: str
    is_relative: bool
    normalized_path: str
    is_reexport: bool
    is_default: bool
    is_aliased: bool
    statement_id: int


class SourceFunction(BaseModel):
    name: str
    visibility: SourceVisibility
    visibility_intent: SourceVisibility
    line_count: int
    declared_args: int
    optional_args: int


class SourceClassMethod(BaseModel):
    name: str
    visibility: SourceVisibility
    visibility_intent: SourceVisibility
    line_count: int
    declared_args: int
    optional_args: int


class SourceClassProperty(BaseModel):
    name: str
    is_optional: bool


class SourceSignature(BaseModel):
    kind: SourceSignatureKind
    line_count: int
    declared_args: int
    optional_args: int


class SourceClass(BaseModel):
    name: str
    visibility: SourceVisibility
    visibility_intent: SourceVisibility
    methods: list[SourceClassMethod]
    properties: list[SourceClassProperty]
    line_count: int


class SourceInterface(BaseModel):
    name: str
    visibility: SourceVisibility
    visibility_intent: SourceVisibility
    methods: list[SourceClassMethod]
    properties: list[SourceClassProperty]
    signatures: list[SourceSignature]
    line_count: int


class SourceType(BaseModel):
    name: str
    visibility: SourceVisibility
    visibility_intent: SourceVisibility
    properties: list[SourceClassProperty]
    signatures: list[SourceSignature]
    line_count: int


class SourceAbstractClass(BaseModel):
    name: str
    visibility: SourceVisibility
    visibility_intent: SourceVisibility
    abstract_methods: list[SourceClassMethod]
    concrete_methods: list[SourceClassMethod]
    properties: list[SourceClassProperty]
    line_count: int


class SourceFile(BaseModel):
    imports: list[SourceImport]
    exports: list[SourceExport] = Field(default_factory=list)
    classes: list[SourceClass]
    interfaces: list[SourceInterface] = Field(default_factory=list)
    types: list[SourceType] = Field(default_factory=list)
    abstract_classes: list[SourceAbstractClass] = Field(default_factory=list)
    functions: list[SourceFunction]
    line_count: int
    code_line_count: int
    public_symbol_count: int
