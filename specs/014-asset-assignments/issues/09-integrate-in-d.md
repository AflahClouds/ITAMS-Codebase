# 09 — Integrate reviewed feature 014 into D locally

**What to build:** Bring the independently reviewed feature 014 from C into D's existing local checkout while preserving feature 013 procurement invoices, existing data, and the local development services.

**Blocked by:** 01–08 — reviewed feature 014 delivery.

**Status:** ready-for-agent

**Requirements:** Existing accepted feature 014 and feature 013 intent; no accepted requirement change.

- [x] Merge reviewed C application and durable feature artifacts into a D development branch with invoice behavior intact and no changes to installed agent/workflow infrastructure.
- [x] Join the D invoice and C custody migration branches without renaming D's applied migration; run merged tests, lint, build, and a migration rehearsal on a database copy.
- [ ] The same independent reviewer assesses the frozen D candidate; the same builder repairs any findings and the same reviewer re-reviews.
- [ ] After clean review, create a fresh durable pre-activation backup, migrate only D's local active database, and verify the existing local services with truthful manual limitations.

## Continuation binding

The current human selected “update this in D” on 2026-10-09. This is a guide-owned local integration continuation after source C's completed native run `95a02038`; it does not reopen or rewrite that run. The exact ten-field canonical builder transition and target payload are preserved below. Assignment ID: `c6f9a9a65782fb8850b4920ff55a381a4b16edbc8fb0a90da03464d7ffeed316`. Payload digest: `150313e3b6fe2cc2953f42ce81c9280e7d490e449df66fc21afad1179f44ff74`.

```json
{"authority_ref":"Verified user decisions in Codex chat 01a0ec71-c1f5-7000-acf8-cd22d304eb43 (Transfer Module update): 2026-09-29 Specify-to-Clarify; Clarify-to-final scope; final clarified scope plus full LOCAL sprint yes at baseline 5de8099386ea20c67be8612a3f608e1db244a3f6, acceptance metadata checkpoint 85be462; 2026-09-30 issue-by-issue runner adaptation; 2026-10-07 proceed compatible upgrade correction and original-scope resume. Revision continuity 877ad2a through 3ed9454 to 3ca461873515a088a689be524191a4981a8da01f verified. Current clarified spec sha256 7f51127d3da454acff721e05d1a051716bbdf693d399cc30190522d203e57cec; plan cee676f4b846c4b1fde0a02eccbdaf2e21435b5452392ed4a3fb2af433982d82; checklist 8879b3d652864e1789d13deffedb565624a3cecdb3723e023f58530e329f3535. Retain durable feature directory. Local-only, no push, remote, merge, release, deployment, publication, living-spec migration or accepted-scope change. This chat 2026-10-08 user recommended selected recorded legacy Transfer date labeled Legacy Transfer event date (event type unverified), followed by explicit proceed approval of concrete Clarify artifacts and resumption under existing local-only authority. Clarification corrects erroneous date provenance within original approved custody design, not a new sprint or timestamp redesign. Retired a7ed8ace before hash edits. Approved clarification checkpoint 6305ce5cfc28518e44d63c6a8b6047d6b61d2b65; byte-preserving unfinished issue06 recovery baseline 61bcd1fde479baf32ebb26bba23c346628b197c5. Tasks sha256 7fcf869af17c937ffb809b0ab9dc8f9d061fe0a92a375ddaca7934f29384fa3a. Same retained native builder/reviewer children; no role substitution or paid/reset capacity. Additional human decision in current chat on 2026-10-09: update this in D:. This grants local integration into a separate development branch and local database/server availability; no main promotion or external authority.","bounded_purpose_description":"Integrate the unchanged reviewed feature014 into the D development checkout, preserve feature013 and local data, verify the combined candidate, repair reviewed findings, and activate the local database/server only after clean review.","bounded_purpose_digest":"6afeea198bae48f0690f251ebad703d745d07716f58f913bef4b6c99c20f9819","expected_head":"ef0f3c231e265f917e4ec191ebd2033bad605d42","new_assignment_id":"c6f9a9a65782fb8850b4920ff55a381a4b16edbc8fb0a90da03464d7ffeed316","payload_digest":"150313e3b6fe2cc2953f42ce81c9280e7d490e449df66fc21afad1179f44ff74","previous_assignment_id":"9fbb1376ecc97b9c27aa315feb34de04dfa3416a1ffcf2ef2e84f614bf8d33cf","rationale":"User explicitly selected D integration; current target is clean committed invoice baseline. High-risk deterministic migration/custody compatibility requires retained builder and independent review; existing gpt-6-sol high assignments remain sufficient and no replacement is needed.","role":"builder","selected_model":"gpt-6-sol"}
```

```json
{
  "action": "Integrate unchanged reviewed feature014 into existing D local server checkout, preserving feature013 invoice behavior and data.",
  "target": "D:\\AFLAH V K\\ITAMS - Codebase",
  "target_head": "ef0f3c231e265f917e4ec191ebd2033bad605d42",
  "source": "C:\\Users\\aflah.vk\\.codex\\worktrees\\asset-assignments\\ITAMS - Codebase",
  "source_head": "7b8bb7e0b15d2d364d97db301925e80d241ce47a",
  "baseline_worktree": "clean",
  "authority": "Current human request: update this in D: (annotation on choice of integrating reviewed feature into original D checkout). Local development branch, local database and server only.",
  "constraints": [
    "preserve committed invoice feature013",
    "preserve local data/media and environment",
    "no main merge or promotion",
    "no remote, push, deployment or release",
    "no accepted requirements rewrite",
    "one writer then same independent reviewer",
    "no live database migration before clean candidate review"
  ]
}
```

## Comments

- Source C reviewed checkpoint: `7b8bb7e0b15d2d364d97db301925e80d241ce47a`, independent same-reviewer clean digest `8e1cc03f87e3326995414acf431ddb3030da6d1dc9b3582e647cb2c021b3c7f9`. D started clean at `ef0f3c231e265f917e4ec191ebd2033bad605d42`; local branch `codex/014-d-local-integration` was created from that exact commit. The merge base was `877ad2a993326d38baa4fc7c9f0d41164b33bc8b`.
- Before integration, D did not resolve the Assignment route and Django detected two asset migration leaves. D's applied `0013_procurementinvoiceversion` remains named and intact. The new no-op `0017_merge_20261009_1504` depends on that invoice migration and the reviewed custody `0016_assetcheckout_reconciliation_provenance` chain. `makemigrations --check --dry-run` and `manage.py check` exited 0.
- Three-way merge retained D's invoice model, serializer, API, storage, and frontend behavior alongside C's custody implementation. The Asset detail/list queryset includes both invoice versions and current Assignment/Checkout prefetches. Reviewed C spec/plan/checklist, CONTEXT, and ADR match source C byte-for-byte; D-managed `.agents/`, `.specify/`, `AGENTS.md`, policy presets and `.gitignore` were restored to D's original bytes. Feature 013 invoice code/storage and procurement frontend paths were preserved.
- Focused merged Django invoice/custody/replay tests: 60/60 exit 0 in 237.211s (`C:\Users\aflah.vk\AppData\Local\Temp\itams-feature014-d-focused.log`). An isolated migration replay regression then demonstrated that restoring the old custody leaf removed D's invoice table (1 expected failure, exit 1); restoring the merged `0017` leaf passed (1/1, exit 0). A public API test of an assigned, invoice-linked Asset's custody projection and protected invoice download passed (1/1, exit 0).
- Complete Django: 354/354, exit 0 in 374.525s (`C:\Users\aflah.vk\AppData\Local\Temp\itams-feature014-d-django-full.log`). Complete frontend: 72/72 across 14 files, exit 0 (`C:\Users\aflah.vk\AppData\Local\Temp\itams-feature014-d-frontend-tests.log`). Lint exit 0 with 13 warnings and no errors (`C:\Users\aflah.vk\AppData\Local\Temp\itams-feature014-d-frontend-lint.log`); build exit 0 with a bundle-size warning (`C:\Users\aflah.vk\AppData\Local\Temp\itams-feature014-d-frontend-build.log`). One component test emitted a nested div-in-p warning; no manual browser acceptance is claimed.
- A consistent SQLite backup copy was migrated in isolation: `C:\Users\aflah.vk\AppData\Local\Temp\itams-feature014-d-pre-migration-20261009-151402.sqlite3`; manifest `C:\Users\aflah.vk\AppData\Local\Temp\itams-feature014-d-pre-migration-20261009-151402.manifest.json`; pristine copy SHA256 `63debc9eae6bac450f00ff3f93b69d072ae8ea6e67cb4cd0ed4b5d3c10d7c5e7`. Invoice, procurement, link, and Asset table counts and row digests matched before/after; SQLite integrity passed. This rehearsal copy is not the fresh pre-activation backup. D's active database has **not** been migrated; a distinct fresh ignored durable backup is required after independent candidate review.
- No push, remote change, main promotion, deployment, release, media/environment replacement, or accepted requirement change occurred. Browser UI and physical custody are unverified.
