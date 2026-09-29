# SQL Layers

- `staging/`: typed, renamed, and code-translated source views
- `marts/`: dimensions, facts, bridge, and business-facing analytical marts
- `analysis/`: readable question-driven SQL used by reports and the dashboard
- `quality/`: zero-row assertions and reconciliation queries

Every SQL file added later must declare its grain, key assumptions, and expected output.
