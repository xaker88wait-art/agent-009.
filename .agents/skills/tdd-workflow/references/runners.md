# Test runner resolution, coverage, and mocks

Reference for the TDD workflow skill. Use to detect the project's test runner,
set coverage thresholds, and mock external dependencies.

## Resolving the test runner

Never assume a default command. Inspect the project's own configuration, in this order:

1. **Package manifest scripts** — e.g. `package.json` → `scripts.test`, or the `[tool.pytest]`/`[tool.coverage]` blocks.
2. **Lockfile / config files** — `pyproject.toml`, `pytest.ini`, `setup.cfg`, `Cargo.toml`, `bunfig.toml`, `vitest.config.*`, `jest.config.*`.
3. **Existing test files** — their import style reveals the framework (e.g. `import { test, expect } from "bun:test"`, `@playwright/test`, `pytest` fixtures).

JavaScript/TypeScript runners:

| Runner | Run once | Watch | Coverage | Lint |
|--------|----------|-------|----------|------|
| npm | `npm test` | `npm test -- --watch` | `npm run test:coverage` | `npm run lint` |
| pnpm | `pnpm test` | `pnpm test --watch` | `pnpm test:coverage` | `pnpm lint` |
| yarn | `yarn test` | `yarn test --watch` | `yarn test:coverage` | `yarn lint` |
| Bun (script runs jest/vitest) | `bun run test` | `bun run test --watch` | `bun run test:coverage` | `bun run lint` |
| Bun (native `bun:test`) | `bun test` | `bun test --watch` | `bun test --coverage` | `bun run lint` |

> `bun test` (Bun's built-in runner) differs from `bun run test` (runs the `package.json` test script). Picking the wrong one is a common failure. Confirm which one the project expects before the RED gate.

Python:
- `pytest` / `pytest -v` / `pytest --cov=<pkg> --cov-report=term-missing` (needs `pytest-cov`).
- Or `unittest` → `python -m unittest discover`.

Rust:
- `cargo test` and `cargo llvm-cov` (or `cargo tarpaulin`).

## Coverage thresholds

80% is the target across branches, functions, lines, and statements. Example task (Jest):

```json
{
  "jest": {
    "coverageThresholds": {
      "global": { "branches": 80, "functions": 80, "lines": 80, "statements": 80 }
    }
  }
}
```

Bun (native): configure in `bunfig.toml` under `[test]` (e.g. `coverageThreshold`), not the Jest config block.

## Mocking external services (JS example)

Isolate unit tests so they don't touch live databases, caches, or third-party APIs:

```typescript
// JSDoc-style mock of a data layer
jest.mock('@/lib/supabase', () => ({
  supabase: {
    from: jest.fn(() => ({
      select: jest.fn(() => ({
        eq: jest.fn(() => Promise.resolve({ data: [{ id: 1 }], error: null }))
      }))
    }))
  }
}))
```

For Bun's native runner use `mock.module(...)` / `mock(...)` from `bun:test` instead of `jest.mock(...)`.

Mock external lookups (embedding API, search, cache) so tests are fast and deterministic, and add a test that exercises the fallback path when the external service is down.

## Common testing anti-patterns

- **Brittle selectors:** prefer roles, labels and `data-testid` over `.css-class-xyz`.
- **Shared mutable state:** give each test its own fixture.
- **Asserting implementation internals:** assert on behavior the user observes.

## CI

Run `<test>` (or `<coverage>`) in CI on every push/PR, and upload coverage (e.g. Codecov) so report drops are caught early.