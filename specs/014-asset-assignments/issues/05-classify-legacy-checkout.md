# 05 — Classify matching legacy Checkout

**What to build:** IT classifies matching open legacy Checkout as Temporary or Ongoing; original issue facts remain and no physical return is invented.

**Blocked by:** 01 — Assign ongoing custody; 03 — Keep temporary Checkout separate.

**Status:** ready-for-agent

**Tasks:** T021–T022 and classification portions of T025–T026. **Requirements:** FR-010–011/013, ALR-001–003; AS-016–017/020–021.

- [x] IT classifies matching open legacy Checkout as Temporary or Ongoing; original issue facts remain and no physical return is invented.
- [x] Mismatch remains Conflicting; unclassified new return/Transfer is blocked; classification records actor/time and cannot duplicate custody.
- [x] Fail-before API/UI tests, focused green exits and a stable local checkpoint are recorded.

## Comments

- Local implementation checkpoint: `c7bd578` (`Implement explicit legacy Checkout classification`). Authorized classification checks the one matching current holder, records the decision actor, time and remarks, and writes audit in the same transaction. Temporary retains the Open Checkout. Ongoing closes it as administrative `Reclassified` without return or inspection and opens one linked Assignment carrying the original issue date, operator, notes and known condition; unknown historical condition remains unknown. A repeat decision does not create another arrangement. The Checkout read model exposes derived current custody so the UI offers classification only for matching Unclassified rows and explains conflicting rows without suggesting a physical Check-in. Reconciliation remains for issue 06.
- Genuine fail-before evidence on 2026-10-08: four new API integration tests exited 1 with four 404 failures for the absent classify endpoint; two new Checkout UI tests exited 1 while the other four passed because classification controls and conflict explanation were absent. A separate read-model assertion exited 1 with `KeyError: current_custody_type`. After the first implementation, a provenance regression exited 1 because an unknown old issue condition was filled from the Asset's current `Average` condition; the narrow correction preserved the blank historical value.
- Focused green: classification API 5/5 exit 0 and Checkout UI 6/6 exit 0. The first full Django run ended with 316 passes and one migration replay error at 317 tests in 609.647s: its 0013 schema was read through the current 0015 model. The replay test now reads its historical model and restores the latest schema; focused migration test 1/1 exit 0, followed by full Django 317/317 OK in 612.020s, exit 0. Full frontend 53/53 across 9 files exited 0; lint exited 0 with 0 errors and 14 existing warnings; Vite build exited 0. `makemigrations --check --dry-run`, worktree and staged `git diff --check` exited 0. Full Django terminal logs are `C:\Users\aflah.vk\AppData\Local\Temp\itams-issue05-full-django.log` (failed run) and `C:\Users\aflah.vk\AppData\Local\Temp\itams-issue05-full-django-rerun.log` (passing run), each with a terminal exit footer.
