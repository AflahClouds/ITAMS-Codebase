# 06 — Open the Confirmation Matching the Procurement Action

**What to build:** Archive opens only its archive confirmation. The singleton
permanent-delete control, including the last-Asset link in Procurement editing,
opens its own clearly named permanent-deletion confirmation. Neither control
lands on the same generic archive page offering both destructive intents.

**Blocked by:** 05 — Open the Retained Asset After Permanent Procurement Release.
**Status:** ready-for-agent
**Traceability:** F002; FR-008; ALR-001; US3; T022–T024.

- [ ] Observe failing regressions through the actual table links and App routes,
  including the edit-form singleton link, before production changes.
- [ ] Archive and permanent-deletion entry points have distinct destinations and
  confirmation text/actions matching the clicked intent.
- [ ] Archive uses only the existing archive request and retains records/links;
  permanent deletion still requires deliberate confirmation and uses only its
  existing singleton permanent-delete request.
- [ ] Preserve permission/cardinality restrictions, retained-Asset navigation,
  cancellation and meaningful server errors; no request occurs merely on entry.
- [ ] Full frontend suite, lint/build pass, relevant current references agree,
  evidence is recorded and a stable candidate is committed/pushed for review.

## Comments

The stakeholder reported that the two buttons link to one page after delivery.
Read-only inspection at c2026c0 confirms both table controls and the singleton
edit link point to /procurement/delete/:id. The component presents an archive
heading plus an optional permanent-delete section. This is a presentation defect
inside the same approved feature's explicit-action requirement, not a change to
the accepted business scope. Original feature-016 design/scope/sprint authority
and this direct correction request authorize its bounded repair; no new product
rule, technology, dependency, deployment or main-promotion authority is inferred.

Use the same bounded native builder and reviewer identities recovered from host
inventory. The prior completed run remains historical; a new native correction
run captures the current exact artifacts/revision rather than resuming a completed
run with stale hashes. Preserve spec/plan/checklist requirements, all historical
evidence and unrelated working-tree/native state. Only frontend action-intent
routing, confirmations, regressions and local evidence are in scope. A query
mode or distinct route may share the component internally, provided each user
entry opens only the intended confirmation and invalid eligibility fails closed.
