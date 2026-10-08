# Minimal assertion proposal, not an applied patch

Primary scope: preserve token units in `aggregate_benchmark.py`.

1. A measured `total_tokens=100` yields 100 tokens regardless of output length.
2. If `total_tokens` is absent but `output_chars=900`, do not emit 900 as token usage. Keep characters in a separately named metric if useful.
3. A measured `total_tokens=0` remains measured zero; it must not trigger a truthiness fallback to characters.
4. Missing or invalid token measurement is represented distinctly from zero and reported with its measurement coverage.
5. An arm with incomplete token measurements must not receive an ordinary numeric token delta against a complete arm. Whether to omit, label unavailable, or introduce a strict-mode error requires upstream agreement and viewer compatibility checks.
6. If both arms have complete numeric token measurements, preserve current mean/stddev behavior and output formatting.

Adjacent proposals are deliberately not bundled: validate grading schema before numeric aggregation; report observed run counts; identify unpaired data; optionally support a planned-run manifest; and represent execution-blocked separately from grade failure. Several already overlap upstream reports and open PRs. Do not open a broad duplicate patch.

Before any implementation: inspect active PR patches for token handling, current schema and viewer consumers; choose the smallest backwards-compatible contract with maintainers. This proposal cannot honestly claim a completed fix or a cleared duplicate check.

## Duplicate-check result

Open PR #1826 already addresses independent token loading and proxy labeling. Use these assertions as review suggestions or independent evidence for that existing PR, not as authorization for a competing patch. Its code was not executed. The documented character proxy is an upstream design choice; improving unavailable-value semantics needs maintainer agreement.
