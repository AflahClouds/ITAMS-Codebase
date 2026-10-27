# 02 — Reject normalized catalog identity conflicts clearly

**What to build:** A maintainer receives a useful and audited name-conflict response, rather than a server error, without losing master identity or references.

**Blocked by:** 01 — Model Brand contract.

**Status:** ready-for-agent

**Traceability:** FR-002–003, ALR-001–003; AS-004–007; T005–T007.

- [ ] Fail-before API tests cover all five masters, creates/renames/self-updates and save-time duplicate races.
- [ ] Whitespace/case identity rules and Brand-scoped Model identity are enforced without changing display casing.
- [ ] Each identity conflict has one durable rejection audit and no partial business mutation.
- [ ] Focused green checks, successor-path cleanup and a development checkpoint are recorded.

## Comments

- Published under the user's accepted feature-015 full local-sprint authority. Execute as one bounded native builder; preserve unrelated work.

