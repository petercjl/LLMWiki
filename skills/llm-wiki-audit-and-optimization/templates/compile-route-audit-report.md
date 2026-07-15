# LLM Wiki Audit Report Template

## 1. Basic Info

- Target path:
- Audit date:
- Audit mode: whole-wiki / domain / topic / post-ingest
- Permission mode: audit-and-optimize / explicit read-only
- Pages inspected:
- Raw/extraction sources sampled:
- Runtime evidence:
- Degraded branches:

## 2. Executive Summary

- Overall readiness: high / medium / low
- Main bottleneck: compile / route / reasoning / input
- Can this wiki support real tasks now? yes / partially / no

## 3. Mechanical Gate

- Formal pages scanned:
- SHELL:
- SKELETON:
- THIN:
- OK:
- Blocked scopes:

## 4. Compile Audit

| Dimension | Score 1-5 | Findings | Evidence / file path | Fix |
| --- | --- | --- | --- | --- |
| Source-to-knowledge transformation |  |  |  |  |
| Depth of reasoning |  |  |  |  |
| Evidence preservation |  |  |  |  |
| Case transferability |  |  |  |  |
| Module boundaries |  |  |  |  |
| Decision process |  |  |  |  |
| Template readiness |  |  |  |  |
| Traceability |  |  |  |  |
| Noise removal |  |  |  |  |
| Actionability |  |  |  |  |

## 5. Route Audit

- Main index quality:
- Domain index quality:
- Learning-path quality:
- Agent template availability:
- Duplicate / overlapping routes:
- Missing route maps:
- Unresolved links / orphans / dead ends:

## 6. Reasoning Readiness

- What user task types are well supported?
- What user task types are weakly supported?
- What inputs would an Agent need from the user?
- What pages should be read first for common tasks?

| Test question | Expected route | Result | Gap |
| --- | --- | --- | --- |
|  |  |  |  |

## 7. Issues

| Priority | Label | Issue | File path | Suggested fix |
| --- | --- | --- | --- | --- |
| P0 |  |  |  |  |
| P1 |  |  |  |  |
| P2 |  |  |  |  |

## 8. Optimizations Applied

| Priority | Repair mode | Issue | Files changed | Result |
| --- | --- | --- | --- | --- |
| P0 |  |  |  |  |
| P1 |  |  |  |  |
| P2 |  |  |  |  |

For explicit read-only runs, write `None — read-only requested` and keep the
proposed repairs in Section 7.

## 9. Changed Files

- Added:
- Updated:
- Moved/retired:
- Unplanned changes: none / list

## 10. Before / After Verification

| Gate | Before | After | Pass |
| --- | --- | --- | --- |
| SHELL / SKELETON / THIN |  |  |  |
| Unresolved links / orphans / dead ends |  |  |  |
| Representative question routes |  |  |  |
| Targeted findings |  |  |  |

## 11. Raw Preservation

- Raw inventory/hash before:
- Raw inventory/hash after:
- Result: unchanged / blocked / not applicable

## 12. Remaining Blockers And Residual Risk

| Priority | Unresolved item | Exact blocker | Required next input/capability |
| --- | --- | --- | --- |
