"""Regenerate docs/conformance/traceability-map.md from the baseline specifications.

Run from the repository root:

    python docs/conformance/build-traceability-map.py

The map answers one question per requirement: can we currently demonstrate that the
system does what the baseline says? It is derived entirely from what the specifications
already assert — the *(Source: ...)* line on each requirement and the bulk mappings in
each §Verified Behavior Evidence section — cross-checked against the test symbols that
actually exist in backend/*/tests.py. Nothing here is inferred from reading application
code; that is the conformance suite's job, not this map's.
"""
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
# A requirement about what a person sees needs a frontend harness, which does not exist.
USER_INTERFACE = re.compile(
    r"frontend|surface|label|control|page |form|visibly|displayed|presentation|menu|route",
    re.I)


def test_symbols():
    found = set()
    for path in glob.glob(os.path.join("backend", "*", "tests.py")):
        text = io.open(path, encoding="utf-8").read()
        found |= set(re.findall(r"^class (\w+)", text, re.M))
        found |= set(re.findall(r"^    def (test_\w+)", text, re.M))
    return found


def collect():
    symbols = test_symbols()
    rows = []
    for path in sorted(glob.glob(os.path.join("specs", "0*", "spec.md"))):
        directory = os.path.basename(os.path.dirname(path))
        if directory not in BASELINE:
            continue  # Change specifications describe unbuilt work by definition.
        code = BASELINE[directory]
        spec = io.open(path, encoding="utf-8").read()

        bulk = {}
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
            cited = set(re.findall(r"::(\w+)", body)) | bulk.get(ident, set())
            cited = sorted(t for t in cited if t in symbols)
            if GOVERNANCE.search(body):
                kind = "governance"
            elif USER_INTERFACE.search(body):
                kind = "ui"
            else:
                kind = "backend"
            if ident in gaps:
                status = "known-gap"
            elif cited:
                status = "test-cited"
            else:
                status = "unverified"
            rows.append([code, directory, ident, kind, status, cited])
    return rows


if __name__ == "__main__":
    data = collect()
    print(f"{len(data)} requirements")
    print("class :", dict(Counter(r[3] for r in data)))
    print("status:", dict(Counter(r[4] for r in data)))
    out = os.path.join("docs", "conformance", "traceability-data.json")
    json.dump(data, io.open(out, "w", encoding="utf-8"), indent=1)
    print("wrote", out)
