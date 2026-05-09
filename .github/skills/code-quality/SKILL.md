---
name: code-quality
description: Validates code correctness, style, and maintainability.
---

<rules>

- annotate using best practices for code quality and maintainability. Be careful about circular import, heavy dependencies in TYPE_CHECKING blocks, and other common code quality pitfalls. If TYPE_CHECKING is used, ensure to import from __future__ import annotations to avoid runtime import issues, don't use string literals for type hints. Always consider the impact of imports on runtime performance and maintainability.
- 