# Output Contract

For complete cards, create a JSON file matching `schema/fact_check_result.schema.json`,
run `scripts/validate_result.py`, then render with `scripts/render_card.py`.

## Required Top-Level Fields

- `metadata`: mode, language, analysis_date, optional topic.
- `content_summary`: short summary of what was checked.
- `overall_verdict`: verdict, confidence_level, summary.
- `claims`: required for quick, standard, and comparison modes.
- `narratives`: required for prebunking mode.
- `sources`: evidence ledger entries.
- `red_flags`: manipulation markers when present.
- `scores`: required for standard and comparison modes; omitted for quick and
  prebunking.
- `share_safe_summary`: copy-ready respectful correction.
- `disclaimer`: AI-assisted analysis and high-stakes caveat.

## Verdict Values

Use one of:

- `confirmed`
- `mostly_true`
- `mixed`
- `unverified`
- `misleading`
- `false`

## HTML Card Sections

The renderer produces these sections when data exists:

1. Header with mode, date, language.
2. Original content summary.
3. Overall verdict and confidence.
4. MFS score and component breakdown for Standard/Comparison modes.
5. Claims breakdown.
6. Active narratives for Prebunking mode.
7. Red flags detected.
8. Evidence ledger / sources used.
9. Educational notes.
10. Share-safe summary.
11. Disclaimer.

## Quick Check Text Format

When not rendering a card, answer with:

```text
Verdict: [verdict] ([confidence])
Why: [1-2 sentences]
Key sources: [2-3 links with tier labels]
Confidence: [one increasing factor; one decreasing factor]
Media-literacy tip: [one short tip]
Share-safe summary: [copy-ready text]
Disclaimer: [one sentence]
```

## Design Requirements

Rendered HTML must be self-contained, mobile-friendly, print-friendly, and usable
without external CSS or JavaScript. Use neutral colors plus verdict colors. Avoid
decorative styling that distracts from evidence.
