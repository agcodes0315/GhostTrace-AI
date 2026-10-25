> **October 25 consolidated build:** 46 unit tests passed; 293 strict provisional classifications, 225 unverified fallbacks; full public-sample fallback status accuracy 22/32, exact-step accuracy 0/32. See `evaluation/evaluation_report.md` for limitations.

# GhostTrace AI — HackerRank Orchestrate October 2026

Evidence-first deletion-audit agent combining exact historical identity resolution, structured evidence snapshots, log-readback correlation, policy handling, and an optional MongoDB Atlas / local Gemma 3:4B policy interpretation demonstration.

## Run

Python 3.12+ recommended. No external API keys are required for the deterministic submission path.

1. Place the organizers' `dataset/` folder beside `code/` at the repository root. Do not include `dataset/` inside `code.zip`.
2. Run `python -m unittest discover -s code/tests -v`.
3. Run `python code/main.py --audit` for the **strict evidence-backed audit**. This deliberately refuses to emit output if coverage is incomplete.
4. **Emergency contest submission fallback only:** `python code/emergency_submit.py`. This writes `output.csv` with all case IDs, preserves all defensible classifications and uses `INCOMPLETE` with empty steps for unresolved cases. It does **not** prove such rows are incomplete and does not satisfy the semantic step contract for those rows. They should not be represented as verified results.
5. Run `python code/validate_output.py` for structural validation only.

### Method

`code/engine.py` parses participant-facing JSON, SQLite-compatible SQL, JSON-lines and correlated log readbacks. Only completed query/readback events with explicit states are admitted. Inferred identity is linked via one trace context, never substring matches. Events occurring after the case audit timestamp are excluded. Atlas / Gemma (`code/atlas_gemma_workflow.py`) are advisory and do not set statuses.

### Important limitations

- The emergency fallback is not a fully evidence-backed deletion audit. In the supplied dataset run, 373 cases remained unresolved.
- PDF and PNG evidence is not integrated into deterministic claims; the parser reports warnings instead of fabricating evidence.
- Search/sync/restore risk correlation and category-specific policy completeness need further work.
- `reported_status` is never treated as proof of deletion.
- Do not upload database passwords, environment files or user data to remote services.

### Files

- `code/main.py`: strict auditor
- `code/emergency_submit.py`: structurally valid emergency fallback (low-accuracy)
- `code/validate_output.py`: exact column/row/step structure validation
- `code/log_evidence.py`: correlated log evidence extractor
- `code/atlas_gemma_workflow.py`: optional policy interpretation demonstration
- `evaluation/evaluation_report.md`: measured evaluation and limitations
- `evaluation/usage_report.md`: costs and call counts for final CSV generation
