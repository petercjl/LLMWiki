# Source Type Profiles

Use this file to route clippings to the right "入脑" method. The core rule: every source type should become AI-usable knowledge, not just a moved file or generic summary.

Never treat "extract" as "shorten." For every source type, preserve all meaningful knowledge units. The output should often be more structured and sometimes longer than the source because it adds interpretation, decision rules, relationship maps, examples, and Agent-usable templates. If a source unit is not represented in formal knowledge, record why.

If no profile fits, use the Unknown Source Type protocol in `SKILL.md`.

## Universal Intake Questions

Ask these for every clipping:

1. What future question should this source help answer?
2. Is this source primarily evidence, instruction, rules, concepts, cases, data, or conversation?
3. Which claims must remain traceable to the raw source?
4. What formal page shape would make this source easiest for a future AI agent to use?
5. Does this source update an existing page, or justify a new page?
6. What headings, tables, examples, code blocks, formulas, images, cases, and limitations must be preserved so no knowledge is lost?
7. What interpretation or enrichment is needed to make implicit logic explicit?

## Profile: Rule / Policy / Reference Documentation

Use for platform rules, official help pages, policy updates, API references, legal/compliance-like rules, tool docs, and pricing/eligibility documentation.

Recommended artifacts:

- Rule summary page
- Rule matrix
- Relationship/conflict matrix
- Tool/entity card
- Decision playbook
- Query entry page

Extract:

- Scope
- Effective dates
- Eligibility
- Definitions
- Formulas
- All examples and sample calculations
- All tables, thresholds, parameters, and edge cases
- Exceptions
- Interactions with other rules/tools
- Risks and consequences
- Required merchant/user actions
- Source update date

Known specialized profile:

- For Taobao/Tmall marketing tools, use `ecommerce-marketing-knowledge-model.md`.

## Profile: Course Transcript / Meeting Transcript

Use for course recordings converted to text, meeting transcripts, interviews, webinars, lectures, and long spoken materials.

Recommended artifacts:

- Source summary under `raw/transcripts/` or `raw/articles/`
- Concept pages for durable ideas
- Playbooks for reusable methods
- Decision pages for commitments or conclusions
- Glossary/entity pages for recurring terms, people, tools, or companies
- Query page when the transcript cluster supports a recurring user question

Extract:

- Speaker/topic structure
- Main thesis
- Reusable frameworks
- Step-by-step methods
- Examples and cases
- Decisions or action items
- Contradictions or unresolved questions
- Terms that deserve glossary/entity pages

Do not preserve filler speech in formal pages. Preserve the full transcript as raw evidence, then compile concise durable knowledge.

Suggested formal structures:

```text
domains/<domain>/learning-paths/<topic>.md
domains/<domain>/playbooks/<method>.md
shared/knowledge-management/<concept>.md
queries/<question>.md
```

## Profile: How-To Tutorial / Operating Procedure

Use for tutorials, setup guides, SOPs, workflows, recipes, or operational instructions.

Recommended artifacts:

- Playbook
- Checklist
- Troubleshooting page
- Tool/entity page

Extract:

- Preconditions
- Inputs
- Steps
- Expected output
- Validation checks
- Failure modes
- Recovery steps
- Commands, code snippets, screenshots, UI paths, and configuration examples
- When not to use the procedure

## Profile: Case Study

Use for brand cases, ecommerce cases, product launches, growth stories, failures, and competitive examples.

Recommended artifacts:

- Case page under the relevant domain
- Entity pages for brands/companies/products
- Pattern page if the case illustrates a reusable principle
- Comparison page if multiple cases are involved

Extract:

- Background
- Strategy
- Tactics
- Constraints
- Results
- Transferable lessons
- Non-transferable context
- Links to related concepts

## Profile: Product / Tool Documentation

Use for SaaS docs, app docs, plugins, APIs, internal tools, agent tools, and platform feature docs.

Recommended artifacts:

- Tool/entity card
- Capability map
- Integration notes
- Playbook
- Troubleshooting page

Extract:

- What the tool does
- Inputs/outputs
- Setup requirements
- Workflows
- Limits
- Risks
- Alternatives
- How it connects to Peter's projects or domains
- All code examples, API request/response shapes, CLI commands, SDK calls, parameters, model/version constraints, and troubleshooting patterns

For product/tool documentation, create a capability map plus code/example section whenever the source contains examples. Do not reduce official docs to a decision summary; preserve reusable invocation templates and source cases.

## Profile: Research / Article / Opinion

Use for essays, research notes, blogs, newsletters, strategy articles, and thought pieces.

Recommended artifacts:

- Concept page
- Argument map
- Comparison page
- Query page for recurring questions

Extract:

- Thesis
- Supporting claims
- Evidence
- Counterpoints
- Assumptions
- Implications for Peter's work
- Open questions

## Profile: Dataset / Table / Report

Use for data-heavy pages, tables, spreadsheets, market reports, rankings, or metrics snapshots.

Recommended artifacts:

- Source summary
- Data dictionary
- Metrics page
- Insight page
- Decision page if it changes action

Extract:

- Table meaning
- Column definitions
- Time period
- Units
- Filters/segments
- Key patterns
- Caveats
- Decisions supported by the data
