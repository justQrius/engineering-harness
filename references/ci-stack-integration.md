# CI Stack Integration

Use this reference when adapting the harness CI job to the repository's actual
tech stack.

## Principle

Split CI into:

- a universal harness job that always runs repo-local workflow checks
- a project job that adapts to the detected stack

This keeps harness upgrades from being tangled with product-language changes.

## Common stack mappings

### Go

- `go vet ./...`
- `go test ./...`
- `GOOS=linux GOARCH=amd64 go build ./...`
- optional: `govulncheck ./...`

### Node / TypeScript

- `npm ci` when a lockfile exists
- `npm test`
- optional: `npm run lint`
- optional: `npm audit --audit-level=high`

### Python

- `python -m pytest`
- optional: `python -m pip install -r requirements.txt`
- optional: `pip-audit`

### Rust

- `cargo test`
- optional: `cargo clippy -- -D warnings`
- optional: `cargo audit`

## Design rule

Prefer repo-local entrypoints such as `task check:harness` and
`task check:project` so local verification and CI are literally the same
commands.