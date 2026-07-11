# Migrating from Modwire 4 to 5

Modwire 5 makes Core an in-memory architecture engine. Filesystem discovery,
configuration-directory loading, code extraction, and writing generated files
belong to `modwire-cli`.

## Architecture reports

Pass an already extracted `QueryableCodeMap` to Core:

```python
from modwire import Modwire
from modwire_extraction.code.query import QueryableCodeMap


def architecture_reports(code_map: QueryableCodeMap):
    return Modwire().architecture().report(code_map)
```

Replace these Modwire 4 APIs:

| Modwire 4 | Modwire 5 |
| --- | --- |
| `Modwire().extract(root, language)` | Let `modwire-cli` own path discovery and extraction, or inject a `QueryableCodeMap`. |
| `ArchitectureApplication.report(root, language)` | `ArchitectureApplication.report(code_map)` |
| `QueryableCodeMapReader.read(root, language)` | Removed from Core. |
| `CodePackageWriter.write(package, destination)` | Removed from Core; writing belongs to CLI. |

## Configuration and serialization

Core retains `from_json`, `to_json`, `from_yaml`, `to_yaml`, `from_dict`, and
`to_dict`. The path-based `load_json`, `save_json`, `load_yaml`, and `save_yaml`
helpers are removed. Read or write files in the CLI boundary and pass strings or
dictionaries to Core.

`ModwireConfig.load_dir()` is also removed. The CLI is responsible for reading
and combining `.modwire` files before constructing the strict in-memory config.

## Dependency graphs and boundaries

Modwire 5 requires `modwire-extraction>=2,<3`. Graph nodes are tracked file IDs;
resolved edges target tracked files, while external and unresolved edges retain
their specifier and explicit resolution state without entering boundary checks.

Boundary rules are closed allowlists:

- same-module tracked dependencies are allowed;
- a tracked cross-module dependency must match an explicit `allow` target;
- external and unresolved edges are ignored by module policy;
- tracked files without a configured module tag produce an unclassified
  violation;
- duplicate tag names remain invalid, while each file may intentionally match
  several distinct tags and realms.
