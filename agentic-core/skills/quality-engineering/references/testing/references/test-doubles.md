# Test doubles

Use a fake, stub, mock, or in-memory resource only when it preserves the contract the test must observe.

- Prefer real local dependencies when they are cheap, deterministic, and relevant.
- Control remote services, nondeterministic time, external I/O, and other boundaries that cannot be made reliable in the test.
- Avoid mocking modules owned by the project when their behavior is part of the contract.
- Assert meaningful interactions only when the interaction itself is required behavior; otherwise assert the observable outcome.
- Prefer an in-memory or dedicated test database, local test server, controlled clock/seed, or temporary directory when it faithfully exercises the contract.
- Tests MUST create their own state and MUST NOT depend on execution order.
