# Coverage Configuration

Use the repository's existing configuration when one exists. Otherwise use the
narrowest command that measures the changed package.

Coverage is diagnostic evidence for unexercised behavior, not a universal quality score. Do not introduce a repository-wide percentage target through this guidance alone; follow an existing project gate or an explicit acceptance requirement.

## Python

```bash
python -m pytest --cov=<package> --cov-report=term-missing
```

Configure `--cov-branch` when branch coverage is part of the project's gate.

## JavaScript or TypeScript

```bash
npx jest --coverage
# or
npx vitest run --coverage
```

## Go

```bash
go test ./... -coverprofile=coverage.out
go tool cover -func=coverage.out
```

Do not invent a coverage command that the project's package manager or CI does
not support. Report missing coverage evidence as a blocker only when the approved
quality gate or acceptance criteria require it.
