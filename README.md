# Skill benchmark evidence-integrity repro

Seven synthetic, black-box fixtures for Anthropic's existing skill-creator aggregator. This is a reproducibility artifact, not a new evaluation engine or a claim about any model's quality.

Known overlapping fixes: [token reporting PR #1826](https://github.com/anthropics/skills/pull/1826) and [sample-count PR #825](https://github.com/anthropics/skills/pull/825), both open when checked on 2026-10-08. This pack adds reproducible evidence, not a novelty claim or a competing fix. Neither PR's code is executed.

## Run

Python 3.10+; standard library only. No package installation, model credentials, browser or network needed by the test program.

```sh
python run_repro.py
cat results/reproduction-check.json
cat results/observations.json
```

The runner replaces only its own seven named fixture folders under `results/`. It executes the vendored upstream script in a subprocess with a restricted environment and captures the actual command, stdout, stderr, exit code, benchmark JSON and Markdown. The script uses no network APIs; OS-enforced network isolation was not independently verified.

## Exact source and license

- Repository: https://github.com/anthropics/skills
- Commit: `683bc88e56f3e09ba94f7055977f3d3aa499f202` (2026-10-05)
- Source: https://github.com/anthropics/skills/blob/683bc88e56f3e09ba94f7055977f3d3aa499f202/skills/skill-creator/scripts/aggregate_benchmark.py
- Git blob: `3e66e8c105be9bab9f0e9c61f0d1482619401580`
- The vendored bytes were retrieved by Git blob and verified using Git's blob SHA-1 construction. SHA-256 is recorded in the result receipt.
- Upstream skill license: Apache-2.0; retained in `vendor/LICENSE.txt`, Copyright 2026 Anthropic, PBC.
- Vendor code is unchanged. The probe and synthetic fixtures were authored for this investigation. The original harness and fixtures are Apache-2.0 licensed; see LICENSE and NOTICE. AI assistance was used to prepare and review this pack. Do not assume every skill in the upstream repository has the same license.

## Observed on 2026-10-08

Every invocation exited 0. Each configuration in the complete control has three runs. Candidate grades are [1, 0, 1]; baseline grades are [1, 1, 1]. The expected complete-data difference is 2/3 - 1 = -1/3.

| Fixture | Actual result | Interpretation |
|---|---|---|
| complete_control | 3 vs 3 runs; pass-rate delta -0.33; token delta +0 | Positive control |
| missing_grading | Remove the candidate's failed grading file: 2 vs 3 runs; warning printed; delta +0.00 | Omission improves the reported mean; an exit-0 report does not establish completeness |
| invalid_schema | Replace one baseline grade with `{}`: baseline mean becomes 0.6667; delta +0.00 | An invalid input is accepted as numerical zero; a schema-validation gap, not a valid-input grading defect |
| blocked_baseline | One baseline grade says execution was blocked but reports passed=true; baseline remains 100% | Semantic control, not a parser exploit: the aggregator trusts the supplied grade and has no typed execution-status gate |
| unbalanced_pairs | Keep only one baseline run: JSON contains 3 vs 1; Markdown still says 3 runs each | Incorrect reported sample count; comparison uncertainty is not surfaced |
| missing_tokens | Remove candidate `total_tokens`; retain 900 output characters | Candidate reports 900 tokens vs measured baseline 100; token delta +800 compares unlike units. Upstream grader documents characters as a proxy; this probe concerns unlabeled aggregation |

These observations do not imply all benchmarks are wrong. The complete control works. Missing-grade warnings exist, and individual JSON run records expose some missing data. The problem is that summary output alone can still look comparable and successful. The blocked case deliberately supplies a dishonest grade; detecting that needs an execution contract, not arbitrary text heuristics.

`planned-runs.json` is this test's oracle, not a documented upstream input. We do not claim the upstream script promises to read it.

The seventh case, `timing_present_tokens_ignored`, adds documented `grading.timing.total_duration_seconds=2` while sibling timing still contains measured `total_tokens=100`. The candidate nevertheless reports 900 tokens and a +800 delta. This is the already-known duration-gating correction covered by PR #1826.

## Most defensible narrow follow-up

Duplicate check found open PR #1826 already addressing token loading and proxy labeling. Do not create a competing patch. The following remains an acceptance-review suggestion for that existing work.

Start with token-unit integrity: `output_chars` is not token usage. Preserve missing tokens as unavailable; report how many runs supplied genuine token measurements; omit a token delta when either compared arm lacks suitable measurements. This should be a small upstream change after reviewing active patches, not another evaluation product.

See `ASSERTION_PROPOSAL.md` for the proposed acceptance contract. No fix is applied here. Current reproduction assertions intentionally verify the observed upstream behaviors so another reader can establish the same result.

## Existing work and contribution boundaries

- https://github.com/anthropics/skills/issues/518 already reports eval-loop and aggregation problems.
- https://github.com/anthropics/skills/issues/1383 already discusses unpaired comparisons and sample-count problems; these are not novel findings.
- Exact token-loading duplicate: https://github.com/anthropics/skills/pull/1826 (head `5e5434d6ab4488f9f5450cda31305ef59f0152e9`) independently loads timing fields and labels proxies. Its code was read, not executed.
- Open PR https://github.com/anthropics/skills/pull/825 explicitly fixes hard-coded run counts and other aggregation issues.
- Open PR https://github.com/anthropics/skills/pull/1602 addresses adjacent benchmark bugs.
- https://github.com/anthropics/skills/pull/1947 already owns the no-subagent fallback proposal.

Do not submit competing fixes for those scopes. The pinned full repository tree had no repository-local contribution or AI policy file matching the standard names checked. That absence is not proof that organization defaults or current submission rules impose no requirements. Recheck before posting and disclose AI-assisted research/code clearly.

## Limits

- No real agent, paid model, private data, or remote side effect was used.
- No alternative evaluator was installed or executed; `agent-skill-eval` was not present. Comparisons of its documented capabilities are not execution evidence.
- This is seven synthetic fixtures on one pinned version, not a representative ecosystem benchmark.
- No adoption, production impact, or economic benefit has been measured. These are characterization tests: a passing run confirms the pinned behavior, not that the behavior is desirable.
- This is independent, unofficial work and is not affiliated with or endorsed by Anthropic.
- Generated results stay local and are excluded from version control. Run commands above to inspect every fixture and actual CLI report.
