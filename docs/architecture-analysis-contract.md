# Architecture analysis contract

`ArchitectureApplication.analyze(code_map)` is the supported, pure analysis
entry point. It accepts an already extracted `QueryableCodeMap` and an
`ArchitectureConfig`; it does not discover source files, read project settings,
persist results, render a representation, or perform transport work.

It returns a versioned `ArchitectureAnalysis` value with deterministic ordered
`outcomes` and `insights`.

Each outcome has one explicit status:

- `pass` — an applicable configured policy produced no violations;
- `violation` — a policy failed, with rule and source evidence;
- `not-applicable` — no policy of that category was configured;
- `unsupported` — a caller or future supported adapter cannot evaluate a
  requested analysis category.

Outcomes always contain a severity and `AnalysisEvidence`. Consumers can branch
on `status`; they never need optional attributes or implementation-specific
report classes to understand the result. Insight payloads are separate from
policy outcomes and retain deterministic report order.

The result schema is currently version `1`. An Agent should depend only on the
public imports re-exported from `modwire_architecture`.
