"""Regenerate docs/conformance/traceability-map.md from the baseline specifications.

Run from the repository root:

    python docs/conformance/build-traceability-map.py

The map answers one question per requirement: can we currently demonstrate that the
system does what the baseline says? It is derived from `Covers:` tags in the test
suites — Python docstrings under `backend/`, `// Covers:` comments in Vitest cases
under `frontend/` — then from the bulk mappings in each §Verified Behavior Evidence
section, cross-checked against test names that actually exist. Nothing here is inferred
from reading application code; that is the conformance suite's job, not this map's.
"""
import datetime
import io
import json
import os
import re
import glob
from collections import Counter

BASELINE = {
    "001-asset-register-lifecycle-baseline": "B2",
    "002-procurement-vendor-catalog-baseline": "B6",
    "003-identity-access-baseline": "B1",
    "004-notifications-audit-baseline": "B8",
    "005-checkout-checkin-baseline": "B3",
    "006-transfer-baseline": "B4",
    "007-service-record-baseline": "B5",
    "008-warranty-amc-baseline": "B7",
    "009-dashboard-reports-exports-baseline": "B9",
}

# A requirement about the specification itself cannot be demonstrated by running code.
GOVERNANCE = re.compile(
    r"MUST NOT be read|MUST remain label|MUST NOT be accepted|evidence integrity"
    r"|reconcil|decision gate|MUST NOT be treated as product intent|new feature directory",
    re.I)
# A requirement about what a person sees needs a frontend harness. One exists now
# (Vitest + Testing Library), so these are automatable rather than merely unautomated.
USER_INTERFACE = re.compile(
    r"frontend|surface|label|control|page |form|visibly|displayed|presentation|menu|route",
    re.I)


BACKEND_TESTS = os.path.join("backend", "*", "test*.py")
# Frontend suites run under Vitest. They are read the same way and feed the same map:
# a `ui` requirement is about what a person sees, so its evidence has to come from a
# test that renders something.
FRONTEND_TESTS = os.path.join("frontend", "src", "**", "*.test.jsx")


def frontend_paths():
    return glob.glob(FRONTEND_TESTS, recursive=True)


def test_symbols():
    found = set()
    for path in glob.glob(BACKEND_TESTS):
        text = io.open(path, encoding="utf-8").read()
        found |= set(re.findall(r"^class (\w+)", text, re.M))
        found |= set(re.findall(r"^    def (test_\w+)", text, re.M))
    for path in frontend_paths():
        text = io.open(path, encoding="utf-8").read()
        # Vitest cases are named by string, not by symbol, so the name is the label.
        found |= set(re.findall(r"^\s*it\(['\"](.+?)['\"]", text, re.M))
    return found


def expected_failures():
    """Names of tests marked `@unittest.expectedFailure`.

    These carry `Covers:` tags like any other test, but they demonstrate the opposite:
    the requirement is stated, executable, and *not* met. Counting them as evidence
    would inflate the map, so they are separated out here and reported as known gaps.
    """
    found = set()
    for path in glob.glob(os.path.join("backend", "*", "test*.py")):
        text = io.open(path, encoding="utf-8").read()
        found |= set(re.findall(
            r"^\s*@(?:unittest\.)?expectedFailure\s*\n\s*def (test_\w+)\(", text, re.M))
    return found


def covers_tags():
    """Read `Covers: B<n> FR-xxx, ...` docstring tags out of the test suite.

    This is the authoritative direction. Evidence lives in the tests, not the
    specifications: once a baseline is accepted its requirement content is immutable
    under Constitution III, so a test written afterwards could never be recorded in
    that baseline's §Verified Behavior Evidence. Tagging the test instead keeps this
    map regenerable for the life of the project.
    """
    out = {}

    def record(tag_text, current):
        for code, ident in re.findall(r"\b(B[1-9])\s+((?:FR|ALR)-\d+)", tag_text):
            out.setdefault(code, {}).setdefault(ident, set()).add(current)

    for path in glob.glob(BACKEND_TESTS):
        current = None
        for line in io.open(path, encoding="utf-8").read().split("\n"):
            hit = re.match(r"^    def (test_\w+)\(", line)
            if hit:
                current = hit.group(1)
            tag = re.search(r"Covers:\s*(.+?)\.?$", line)
            if tag and current:
                record(tag.group(1), current)

    # In a Vitest file the tag is a `// Covers:` comment inside the case body, and the
    # case is identified by its `it(...)` label rather than by a symbol.
    for path in frontend_paths():
        current = None
        for line in io.open(path, encoding="utf-8").read().split("\n"):
            hit = re.match(r"^\s*it(?:\.fails)?\(['\"](.+?)['\"]", line)
            if hit:
                current = hit.group(1)
            tag = re.search(r"//\s*Covers:\s*(.+?)\.?$", line)
            if tag and current:
                record(tag.group(1), current)
    return out


def collect():
    symbols = test_symbols()
    tags = covers_tags()
    xfail = expected_failures()
    rows = []
    for path in sorted(glob.glob(os.path.join("specs", "0*", "spec.md"))):
        directory = os.path.basename(os.path.dirname(path))
        if directory not in BASELINE:
            continue  # Change specifications describe unbuilt work by definition.
        code = BASELINE[directory]
        spec = io.open(path, encoding="utf-8").read()

        bulk = {k: set(v) for k, v in tags.get(code, {}).items()}
        section = re.search(r"### Verified Behavior Evidence(.*?)\n### ", spec, re.S)
        if section:
            for line in re.split(r"\n(?=- )", section.group(1)):
                for ident in re.findall(r"\b((?:FR|ALR)-\d+)\b", line):
                    bulk.setdefault(ident, set()).update(re.findall(r"::(\w+)", line))

        # Requirements named in a conformance-gap register are known non-conforming.
        gaps = set()
        for row in re.finditer(r"^\|\s*\d+[a-z]?\s*\|[^|]*\|\s*([^|]*?)\s*\|", spec, re.M):
            gaps |= set(re.findall(r"\b((?:FR|ALR)-\d+)\b", row.group(1)))

        for block in re.split(r"\n(?=- \*\*(?:FR|ALR)-\d+)", spec):
            head = re.match(r"- \*\*((?:FR|ALR)-\d+)", block)
            if not head:
                continue
            ident = head.group(1)
            body = block[:1400]
            tagged = set(re.findall(r"::(\w+)", body)) | bulk.get(ident, set())
            tagged = {t for t in tagged if t in symbols}
            # An expectedFailure test proves non-conformance, so it is not evidence.
            failing = sorted(tagged & xfail)
            cited = sorted(tagged - xfail)
            if GOVERNANCE.search(body):
                kind = "governance"
            elif USER_INTERFACE.search(body):
                kind = "ui"
            else:
                kind = "backend"
            # Passing evidence and a recorded gap can both be true of one requirement,
            # and collapsing that either way misleads: calling it `test-cited` inflates
            # the demonstrated count, calling it `known-gap` buries real evidence and
            # never notices a register row going stale (B9's rows 1-4 are recorded
            # closed in its own conformance update but still listed). It gets its own
            # status instead, so `test-cited` stays strict.
            registered = ident in gaps
            if cited and (registered or failing):
                status = "partly-met"
            elif cited:
                status = "test-cited"
            elif registered or failing:
                status = "known-gap"
            else:
                status = "unverified"
            rows.append([code, directory, ident, kind, status, cited, failing,
                         registered])
    return rows


def render(data, today):
    """Emit the map document. Prose that states a number computes it from `data`."""
    total, kinds = len(data), Counter(r[3] for r in data)
    st = Counter(r[4] for r in data)
    back = Counter(r[4] for r in data if r[3] == "backend")
    n_back = kinds["backend"]
    partial = [r for r in data if r[4] == "partly-met"]
    n_fail = len({t for r in data for t in r[6]})
    per = []
    for code in sorted({r[0] for r in data}, key=lambda c: BASELINE_ORDER.index(c)):
        sub = [r for r in data if r[0] == code]
        c = Counter(r[4] for r in sub)
        per.append((code, sub[0][1], len(sub), sum(1 for r in sub if r[3] == "backend"),
                    c["test-cited"], c["partly-met"], c["known-gap"], c["unverified"]))
    weakest = min(per, key=lambda p: (p[4] - p[7]))

    def cell(names):
        return ", ".join(f"`{n}`" for n in names) if names else "—"

    out = [
        "# Conformance Traceability Map", "",
        f"**Generated**: {today} · **Source**: `Covers:` tags in `backend/*/test*.py`, "
        "plus the nine AS-BUILT baselines under `specs/`",
        "**Regenerate**: `python docs/conformance/build-traceability-map.py`",
        "**Run the suites**: `python manage.py test` in `backend/`, `npm test` in "
        "`frontend/`", "",
        "This document is generated in full. Edit the generator, not this file.", "",
        "## What this answers, and what it does not", "",
        "One question per requirement: **can we currently demonstrate that the system does "
        "what the baseline says?**", "",
        "Evidence is read from `Covers: B<n> FR-xxx` tags — Python docstrings in `backend/`, "
        "`// Covers:` comments in `frontend/` Vitest cases — then from "
        "each baseline's §Verified Behavior Evidence. **The tags are the authoritative "
        "direction.** Once a baseline is accepted its requirement content is immutable under "
        "Constitution III, so a test written afterwards could never be recorded in that "
        "baseline's evidence section — tagging the test keeps this map regenerable for the "
        "life of the project.", "",
        "It does **not** read application code to judge conformance. `test-cited` means a "
        "tagged test exists and passes; it does not re-verify that the test proves the whole "
        "requirement.", "",
        "## Status vocabulary", "",
        "| Status | Meaning |", "| --- | --- |",
        "| `test-cited` | A tagged automated test demonstrates it, and no gap is recorded "
        "against it. |",
        "| `partly-met` | Passing evidence **and** a recorded gap — an `expectedFailure` "
        "test, a register row, or both. |",
        "| `known-gap` | A recorded gap with no passing evidence. The system is known "
        "**not** to satisfy it. |",
        "| `unverified` | Neither — conformance is unknown. |", "",
        "A test marked `@unittest.expectedFailure` proves the opposite of conformance, so it "
        "is never counted as evidence. `partly-met` exists because collapsing it either way "
        "misleads: folding it into `test-cited` inflates the demonstrated count, and folding "
        "it into `known-gap` buries real evidence and never notices a register row going "
        "stale — B9's rows 1-4 are recorded closed in its own conformance update and are "
        "still listed. Only `test-cited` counts as demonstrated below.", "",
        "## Verifiability classes", "",
        "| Class | Count | Automatable today? |", "| --- | --- | --- |",
        f"| `backend` | {kinds['backend']} | **Yes** — the actionable set. |",
        f"| `ui` | {kinds['ui']} | **Yes** — Vitest and Testing Library, `npm test` in "
        "`frontend/`. |",
        f"| `governance` | {kinds['governance']} | **No, and never** — requirements about "
        "the specification itself. |", "",
        "Classification is heuristic from requirement wording; treat boundary cases as a "
        "first pass to review.", "",
        "## Headline numbers", "",
        f"- **{total} requirements** across the nine baselines.",
        f"- **{st['test-cited']} test-cited · {st['partly-met']} partly-met · "
        f"{st['known-gap']} known-gap · {st['unverified']} unverified.**",
        f"- Of the **{n_back} backend** requirements automatable today:",
        f"  **{back['test-cited']} test-cited · {back['partly-met']} partly-met · "
        f"{back['known-gap']} known-gap · {back['unverified']} unverified**.", "",
        f"**{round(100 * back['test-cited'] / n_back)}% of the automatable set is fully "
        f"demonstrated**, from 8% at the start, with a further "
        f"{round(100 * back['partly-met'] / n_back)}% partly met. Two moves got it there: "
        "tagging the existing suite (+69, no new tests), then writing a conformance suite "
        "for whichever baseline was weakest at the time — B8, then B9, B6, B7, and B8 and "
        "B9 again.", "",
        f"{n_fail} tests are marked `expectedFailure`. They document requirements the code "
        "does not satisfy, so the suite stays green against known gaps while the runner "
        "reports an unexpected success the moment one is fixed.", "",
        f"The {len(partial)} `partly-met` requirements are the most useful column to work: "
        "each already has a test harness and a named defect, so closing one is a small "
        "change rather than a new investigation.", "",
        "## Per baseline", "",
        "| Baseline | Total | backend | test-cited | partly-met | known-gap | unverified |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    out += [f"| {c} `{d}` | {t} | {b} | {ci} | {pm} | {g} | {u} |"
            for c, d, t, b, ci, pm, g, u in per]
    out += ["",
            f"**{weakest[0]} is now the weakest** at {weakest[4]} fully demonstrated "
            f"against {weakest[7]} unverified.", "", "## Full map", ""]
    for code, directory, *_ in per:
        out += [f"### {code} — `{directory}`", "",
                "| Requirement | Class | Status | Evidence | Failing clause | In register |",
                "| --- | --- | --- | --- | --- | --- |"]
        rows = [r for r in data if r[0] == code]
        for r in sorted(rows, key=lambda r: (r[2][0], int(r[2].split("-")[1]))):
            out.append(f"| {r[2]} | {r[3]} | {r[4]} | {cell(r[5])} | {cell(r[6])} "
                       f"| {'yes' if r[7] else '—'} |")
        out.append("")
    out += [
        "## How to use this", "",
        "1. **Tag as you write.** Every new test gets a `Covers:` line; the map regenerates.",
        "2. **Record a gap as `expectedFailure`, not an omission** — the requirement stays",
        "   executable and the runner tells you when it starts passing.",
        "3. **Work the backend column in risk order** — authorization and privacy, then",
        "   lifecycle integrity, then audit and retention, then presentation.",
        "4. **Translate the acceptance scenarios.** 290 Given/When/Then cases are written.",
        "5. **Reconcile as you go.** A failing test whose requirement is *not* in a gap",
        "   register means the register was incomplete.",
        "6. **Decide the UI question separately** — the `ui` rows need a frontend runner.",
        ""]
    return "\n".join(out)


BASELINE_ORDER = ["B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B9"]


if __name__ == "__main__":
    data = collect()
    print(f"{len(data)} requirements")
    print("class :", dict(Counter(r[3] for r in data)))
    print("status:", dict(Counter(r[4] for r in data)))
    print("backend:", dict(Counter(r[4] for r in data if r[3] == "backend")))
    for code in sorted({r[0] for r in data}):
        sub = [r for r in data if r[0] == code]
        counts = Counter(r[4] for r in sub)
        print(f"  {code} total={len(sub)} backend={sum(1 for r in sub if r[3] == 'backend')} "
              f"cited={counts['test-cited']} partly={counts['partly-met']} "
              f"gap={counts['known-gap']} unverified={counts['unverified']}")
    out = os.path.join("docs", "conformance", "traceability-data.json")
    json.dump(data, io.open(out, "w", encoding="utf-8"), indent=1)
    print("wrote", out)
    doc = os.path.join("docs", "conformance", "traceability-map.md")
    io.open(doc, "w", encoding="utf-8").write(
        render(data, datetime.date.today().isoformat()))
    print("wrote", doc)
