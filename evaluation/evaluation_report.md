# GhostTrace — Consolidated Evaluation (25 October 2026)

## Protocol

The production 518-case input is predicted using participant-facing evidence only. Public sample labels are used solely for evaluation. `emergency_submit.py` writes structurally valid `INCOMPLETE` / empty-step fallbacks for cases that the strict evidence auditor declines to classify. Such rows are **not verified** and must never be represented as definitive deletion verdicts.

## Measured results (this exact package)

| Metric | Value |
|---|---:|
| Unit tests | **46/46 passed** |
| Full dataset output | 518 unique requests |
| Strict provisional cases | 293 / 518 |
| Unverified fallback cases | **225 / 518** |
| CSV structural validation | PASS |
| Public sample strict predictions | 12 / 32 |
| Strict status correct among predictions | 8 / 12 = 66.67% |
| Strict status correct across all samples | 8 / 32 = 25.00% |
| Strict exact step arrays | 0 / 12 = 0% |
| Strict operation-sequence accuracy | 1 / 12 = 8.33% |
| Public sample fallback status correct | 22 / 32 = 68.75% |
| Public sample fallback exact step arrays | 0 / 32 = 0% |
| Full-case step-field accuracy | Not measurable without evaluation labels |

This is not independently verified correctness on unseen evaluation data. A 518-row structurally valid CSV does not imply every result is supported by evidence.

## Consolidated implementation changes

1. Expanded deletion-intent recognition with explicit negation controls; previously mistaken `NOT_APPLICABLE` classifications are not silently restored.
2. Parse timestamped structured readbacks from plain logs and JSON service exports.
3. Parse nested `snapshots -> records` with snapshot-specific capture time, source system and resource IDs; avoid assuming an empty snapshot proves absence.
4. Handle explicit inactive connectors, active restore risks, and observed data-flow states conservatively.
5. Include already-compliant resources in final verification plans for incomplete cases while keeping prospective verification `evidence_id` empty.
6. Leave uncertain ownership, unknown states, missing evidence and unsupported PDF/PNG text for review. No invented evidence citations.

## Three participant-authored regression cases

- A 404 with a null profile can prove absence of that specific resource; HTTP 200 alone is insufficient to prove presence.
- An enabled connector that is matched by an exact subject identifier creates a synchronization risk and needs a disable/verify plan.
- An incomplete case with a present search record and an already-absent account must include verification of both records. See `test_incomplete_verification.py`.

## Known limitations

- **225 unresolved requests** remain; 233 cases were previously without attributable evidence, and the consolidated parser reduces but does not eliminate that deficit.
- PDF and PNG evidence is not automatically converted to independently verifiable ownership/state observations.
- Complete-case proof requires a full resource inventory and no overlooked copy or restore path; this implementation cannot guarantee that inventory is exhaustive.
- Exact step-array accuracy on public samples remains 0%; therefore, this should be regarded as an emergency submission candidate, not a verified winning solution.
