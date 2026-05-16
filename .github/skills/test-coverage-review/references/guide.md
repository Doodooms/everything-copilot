# Test Coverage Review Guide

Use this guide when the workflow needs a reminder of the legacy test-coverage-review responsibilities.

- Start from the changed behavior, not from the test count.
- Check whether tests would actually catch the regression implied by the change.
- Review edge cases and failure paths that materially affect correctness.
- Reward strong assertions, not incidental execution.
- Report positive coverage only when it clearly reduces regression risk.