# LLM Wiki Optimization Workflow

Use this reference after the main audit has produced a path-specific issue
inventory and the request is not explicitly read-only.

## Contents

1. Repair mode selection
2. Routing and status repair
3. Formal synthesis repair
4. Full source recompile
5. Memory reorganization
6. Verification and return rules

## 1. Repair Mode Selection

Choose the smallest mode that resolves each finding:

| Finding | Mode | Required evidence |
| --- | --- | --- |
| Broken link, missing route, stale index/status | Routing and status | Existing source page and intended target |
| Thin or shell formal page with complete notes | Formal synthesis | Extraction notes and source anchors |
| Incomplete notes, missing coverage, failed semantic validation | Full source recompile | Preserved raw source and current ingest workflow |
| Duplicated, source-shaped, or misplaced knowledge | Memory reorganization | Existing pages, provenance, routes, and durable destination |

Do not turn a navigation defect into a content rewrite. Do not disguise a shell
page by adding generic prose. A single run may use several modes, but complete
and verify one coherent source/topic scope before moving to another.

## 2. Routing And Status Repair

For each confirmed route defect:

1. locate the real target page; never create a fake target only to clear a link;
2. use a stable Wiki-relative link that resolves from the source page;
3. add missing entries to the narrowest useful domain, topic, or query index;
4. remove or relabel misleading routes to unpopulated skeletons;
5. keep `blocked`, source-less, and audit-only pages out of ordinary query and
   answer routes; point normal routes only at usable evidence-bearing pages;
6. change status only when the underlying content supports it;
7. preserve knowledge prose unless the defect is in that prose;
8. update `log.md` when the Wiki's rules require meaningful repair logging.

Re-read the changed pages and rerun route checks immediately. Return to the main
workflow's re-audit step after all route findings in scope are addressed.

## 3. Formal Synthesis Repair

Use only when extraction notes and source evidence can support the rebuilt page.

1. map each weak page to knowledge units and source evidence;
2. rebuild reasoning, decisions, conditions, boundaries, examples, and anchors;
3. preserve valid claims, provenance, and routes;
4. record omissions or uncertainty instead of silently filling gaps;
5. remove classroom/source logistics from durable pages unless they are useful
   knowledge;
6. compare every sentence added during synthesis with the declared source;
   delete or qualify plausible-sounding consequences, examples, or advice that
   the source does not actually support;
7. update affected indexes and query routes after synthesis passes review.

If the notes cannot support the repair, switch that finding to full source
recompile. Never improvise knowledge from the page title alone.

## 4. Full Source Recompile

Use when the existing extraction package is incomplete or invalid.

1. identify the original source and current extraction package;
2. hash or otherwise record raw material before work;
3. resolve the current installed `llm-wiki-ingest` by Skill identity and read its
   current adapter, semantic-validation, coverage, and audit-handoff contracts;
4. recompile one existing source package at a time;
5. preserve the previous formal package until the replacement passes its gates;
6. compare rebuilt claims and coverage against source evidence;
7. update routes and status only after the replacement is verified;
8. confirm raw material is unchanged.

Do not depend on historical extraction filenames. If the ingest Skill, required
adapter, raw source, or confirmed extraction tool is unavailable, mark only this
branch blocked and continue with independent repairs.

## 5. Memory Reorganization

Use for knowledge that exists but is difficult to retrieve because it is
duplicated, source-shaped, course-shaped, or placed under the wrong durable topic.

Build this migration table as an internal execution plan; do not stop for
confirmation unless the user explicitly requested a preview-only run:

| Existing page | Current role | Durable home | Merge, move, split, or link | Provenance kept at |
| --- | --- | --- | --- | --- |

Then:

1. reconstruct thin material before moving it;
2. classify by durable topic and business use rather than by source title;
3. link pages that provide distinct context;
4. merge only true duplicates after preserving every unique knowledge unit;
5. keep raw sources and extraction notes in place;
6. prefer a provenance pointer or redirect page over unexplained deletion;
7. update root/domain/query routes and backlinks;
8. remove stale route residues after the new route passes verification.

Formal pages may be retired only after their replacement is complete, routes
resolve, and provenance remains discoverable. Raw files are never retired here.

## 6. Verification And Return Rules

For every repair mode, verify:

- every targeted issue is resolved or has a concrete blocker;
- no new unresolved link, orphan, dead end, shell, or thin formal page was
  introduced;
- every formal claim on finding pages, changed pages, and representative answer
  routes remains traceable to notes or raw evidence, including claims left by
  earlier runs;
- unsupported formal claims are removed, qualified, or blocked even when they
  were not edited during the current repair;
- blocked, source-less, and audit-only pages are absent from ordinary answer
  routes even when they remain discoverable for maintenance;
- noisy ASR/OCR material retains passed semantic validation;
- raw hashes or contents are unchanged;
- actual changes match the issue inventory;
- at least one previously weak ordinary question or route now works.

If an applicable gate fails, repair the cause and rerun that gate. Return to the
main Skill's re-audit step only when the current mode is stable or blocked by a
named missing input or capability.

Mechanical and route success never overrides a failed source comparison.
