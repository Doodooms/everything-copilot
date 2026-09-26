# Test Templates

Use the target repository's existing naming and assertion style first. These are
fallback templates for a repository that has no established local pattern.

Test selection and behavioral adequacy belong to the `testing` skill. These
examples provide framework syntax only; keep scenarios and assertions aligned
with the repository's approved contract and existing conventions.

## Python with pytest

```python
def test_returns_results_for_valid_query():
    result = search("login")
    assert result
    assert result[0]["score"] > 0.7


def test_rejects_empty_query():
    with pytest.raises(ValueError, match="query cannot be empty"):
        search("")
```

## TypeScript with Jest or Vitest

```typescript
describe("search", () => {
  it("returns results for a valid query", async () => {
    const results = await search("login");
    expect(results.length).toBeGreaterThan(0);
    expect(results[0].score).toBeGreaterThan(0.7);
  });

  it("rejects an empty query", async () => {
    await expect(search("")).rejects.toThrow("query cannot be empty");
  });
});
```

## Go

```go
func TestSearch_ReturnsResultsForValidQuery(t *testing.T) {
    results, err := Search("login")
    if err != nil {
        t.Fatal(err)
    }
    if len(results) == 0 {
        t.Error("expected results")
    }
}
```
