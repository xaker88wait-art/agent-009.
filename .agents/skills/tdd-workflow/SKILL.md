---
name: tdd-workflow
description: This skill should be used when the user asks to "write tests first", "follow TDD", "use test-driven development", "add tests before implementing", "fix a bug with tests", or wants test coverage on new features, bug fixes, or refactors. Enforces writing tests before implementation code with an 80%+ coverage target.
---

# Test-Driven Development Workflow

Drive all code changes through a RED-GREEN-REFACTOR loop: write a failing test first, implement the minimum code to pass it, then refactor with the suite still green. Treat tests as the safety net that makes confident refactoring and reliable delivery possible.

## When to Use

- Adding new features or functionality
- Fixing bugs
- Refactoring existing code
- Adding or changing API surface
- Extracting or restructuring components

## Core Principles

1. **Write tests before code.** Start with the expected behavior as a failing test (RED), then implement (GREEN), then clean up (REFACTOR).
2. **Aim for 80%+ coverage** across unit and integration tests.
3. **Test behavior, not implementation details.** Assert on user-visible behavior and public interface, never on internal state or private methods.
4. **Keep tests independent.** Each test sets up its own data; no test should depend on another one's side effects.
5. **Test the edge cases**, not just the happy path: null, empty, invalid, boundary, and error paths.

## Workflow Steps

1. **Resolve the test runner.** Inspect how the project actually runs tests (`package.json` `scripts.test`, `pyproject.toml`/`pytest.ini`, `Cargo.toml` + `[dev-dependencies]`, etc.). Use the detected runner directly; never assume `npm test`. Substitute the real command wherever a `<test>` placeholder appears below.
2. **Write the failing test.** Describe one behavior per test with `arrange-act-assert`. Name each test to say what it verifies.
3. **Run the test and confirm it fails (RED).** A test that cannot fail proves nothing.
4. **Implement the minimum code** to make it pass (GREEN).
5. **Run the test again and confirm it passes.**
6. **Refactor** while keeping the suite green: remove duplication, improve names, simplify.
7. **Verify coverage** meets the 80% threshold; add tests for uncovered branches.

Follow the cycle for each unit of behavior rather than writing a large implementation all at once.

## Testing Patterns

- **Unit tests** — functions, utilities, pure logic, component logic.
- **Integration tests** — API endpoints, database operations, service-to-service interactions.
- **End-to-end tests** — critical user flows and complete workflows via the browser.

Isolate unit tests by mocking external dependencies (databases, caches, third-party APIs); verify fallback behavior by making the mock fail.

## Organizational Guidance

Colocate test files next to the code they cover when the framework convention supports it (e.g. `Button.tsx` → `Button.test.tsx`), or in a dedicated `tests/`/`test/` directory. Keep a separate `e2e/` folder for end-to-end specs. Each test is responsible for its own fixtures and cleanup.

## Common Mistakes to Avoid

- **Testing implementation details** — e.g. asserting on internal component state instead of rendered output.
- **Brittle selectors** — prefer roles, labels, and `data-testid` over unstable class names.
- **Missing isolation** — tests writing shared state and depending on order.
- **Skipping the RED step** — writing code first and tests as an afterthought.
- **Ignoring coverage reports** — leaving branches untested.
- **Committing in a red state** — never commit with failing tests (pre-commit hook should run `<test>` and lint).

## Verification

- 80%+ coverage achieved (unit + integration).
- All tests green; no `skip`/`disabled`/`only` left behind.
- Fast unit tests (<50 ms each; whole unit suite <30 s).
- E2E covers the critical user flows.
- Tests catch real bugs before they reach the main branch (run in CI).

## Language-specific runner guidance

Language and framework specifics (detecting the runner, coverage thresholds, common mocks) are in `references/runners.md`. Consult it before starting in an unfamiliar stack.

## Additional Resources

### Reference Files
- **`references/runners.md`** — resolving the test runner, coverage thresholds, and common mocking patterns across languages.

> Adapted from the `tdd-workflow` skill in `affaan-m/ECC` (MIT); rewritten for any language and in this workspace's skill format.