# Fact-Check Workflow

## Intake

Identify the input before analysis:

- Pasted claim, quote, article, or social media post.
- URL or set of URLs.
- Screenshot or image with visible text.
- Two sources for comparison.
- Topic query for prebunking.

For images, extract visible text and separately note whether the image itself may
need verification: platform, author/date metadata, crop context, visible edits,
and whether reverse image search would be useful.

## Claim Decomposition

Break the input into checkable units and label each item.

| Type | Code | Action |
| --- | --- | --- |
| Factual claim | F | Verify with evidence |
| Statistical claim | S | Verify data, denominator, timeframe, method |
| Implied claim | I | Restate the implied factual claim and verify it |
| Opinion/value judgment | O | Mark as not checkable |
| Prediction/future claim | P | Mark as not yet verifiable unless it contains present facts |
| Vague/unfalsifiable | U | Mark as not checkable; explain what would be needed |

Most false or misleading content mixes true, false, and opinion elements. Assign
per-claim verdicts before assigning an overall verdict.

## Standard Fact-Check Pipeline

1. Decompose claims.
2. Search in the original language and in English.
3. Add Russian, German, French, or other languages when origin, region, or policy
   context warrants it.
4. Search for exact phrases, neutral formulations, and the opposite claim.
5. Build an evidence ledger.
6. Evaluate key sources with lateral reading.
7. Trace origin when the claim appears viral, translated, or campaign-like.
8. Scan for red flags.
9. Assign per-claim verdicts and confidence.
10. Calculate MFS for a full card.
11. Produce share-safe summary and educational notes.

## Quick Check

Use Quick check only for a narrow claim. Include:

- Verdict and confidence.
- One to two sentence explanation.
- Two or three key sources with tier labels.
- One short confidence calibration note.
- One relevant media-literacy tip.
- Share-safe summary.
- Short disclaimer.

Do not calculate MFS in Quick mode. Upgrade to Standard when there are multiple
claims or important nuance.

## Comparison Mode

For two sources:

1. Decompose both sources independently.
2. Build an agreement/disagreement matrix:
   - Agreed facts.
   - Direct contradictions.
   - Claims exclusive to source A.
   - Claims exclusive to source B.
3. Evaluate each source's evidence quality and transparency.
4. Investigate contradictions with independent sources.
5. Conclude which source is more reliable, or state that neither is adequately
   supported.

## Prebunking Mode

Use prebunking when the user asks about narratives around a topic rather than a
specific claim.

1. Search for current documented false narratives.
2. Prefer recent fact-checks, EUvsDisinfo, Google Fact Check Explorer snippets,
   official sources, and reputable journalism about disinformation campaigns.
3. Document three to seven narratives when available.
4. For each narrative, record:
   - Core false or misleading claim.
   - Manipulation technique codes.
   - Spread level: high, medium, low, or unknown.
   - Factual counter-evidence.
   - Defensive tip.
5. Do not calculate MFS; there is no single analyzed content item.

## Web-Unavailable Fallback

If live web access is unavailable:

- State that the analysis is not live-verified.
- Use only stable background knowledge and clearly mark it as provisional.
- Lower confidence by at least one level.
- Give the user specific searches and primary sources to check.
- Do not claim that a recent event or current statistic is verified.
