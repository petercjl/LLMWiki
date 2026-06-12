# Spreadsheet and Report Adapter

Use for Excel, CSV, TSV, exported dashboards, analysis reports, and table-heavy sources.

## Intake

Record:

- file path and format
- workbook sheets or table names
- row/column counts
- detected headers
- units, date ranges, currency, filters
- formulas/pivots/charts if present
- data sensitivity

For spreadsheets, prefer structured parsing over copy-paste extraction.

## Inventory

Inventory at the right level:

- workbook/sheet metadata
- table schema
- metric definitions
- row groups or segment-level records
- formulas and derived fields
- charts and their visible findings
- footnotes, filters, caveats
- outliers, thresholds, decision rules

Do not create one source unit per row for huge datasets unless rows are individually meaningful. Use grouped coverage plus preserve raw data.

## Formal Output

Choose:

- metric dictionary
- analysis report
- decision page
- operating dashboard guide
- data source card
- playbook/checklist

Keep formulas, units, thresholds, and caveats explicit. Distinguish source data from interpretation.

## Validation

Verify every sheet/table is represented. Check that totals, units, filters, formulas, and chart conclusions are recoverable without reopening the spreadsheet.
