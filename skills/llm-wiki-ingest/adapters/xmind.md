# XMind Adapter

Use for `.xmind` mind maps and exported mind-map structures.

## Intake

Record:

- file path
- workbook title
- sheet names
- root topics
- whether attachments, notes, markers, links, labels, or images exist
- extraction method and parser success

Prefer `scripts/extract_xmind.py` to produce a deterministic topic tree before interpretation.

## Inventory

Every node is a source unit.

Track:

- node ID
- node path from root
- depth
- title text
- parent ID
- notes
- labels
- markers
- links
- attached image/file references
- relationship lines and summaries, if extractable
- image source path for screenshot/diagram nodes

Do not ingest only leaf nodes. Parent structure is knowledge because it encodes classification and reasoning.

## Reconstruction Logic

XMind sources are usually fragments, not prose. Do not compile them by flattening nodes into a list.

Before formal writing:

1. Read the whole tree and infer the root question the map answers.
2. Identify top-level branches as argument modules, not ordinary headings.
3. For each branch, infer its local question: comparison, recommendation, workflow, platform-specific procedure, exception, or evidence.
4. Preserve every node as coverage, but synthesize branch fragments into connected paragraphs, tables, checklists, and decision rules.
5. When multiple XMind files are versions of the same tree, compute the superset tree and record which files contain each node. Do not duplicate shared nodes as separate knowledge.
6. Treat screenshots as knowledge units. If screenshot text/path cannot be extracted, preserve image assets and mark the exact UI path as `unresolved`, not silently omitted.

## Formal Output

Choose:

- taxonomy/concept map
- project plan
- playbook/checklist
- decision tree
- learning path
- entity map

Preserve hierarchy in formal pages, but enrich it into Agent-usable rules and workflows when the map is shorthand.

## Validation

Node count in source inventory must match extracted node count. Every top-level branch must have a formal destination or an explicit raw-only/omitted reason.
