# Misinformation Friction Score Calibration

MFS is a heuristic communication-risk score, not a probability and not a formal
classifier. Use it only for Standard and Comparison cards.

## Formula

`MFS = CFS * 0.50 + MTS * 0.30 + SCD * 0.20`

- CFS: Claim Falsehood Score. How false or unsupported are the factual claims?
- MTS: Manipulation Technique Score. How strongly does the content use red flags?
- SCD: Source Credibility Deficit. How weak, opaque, or non-independent are the
  sources?

Round to the nearest whole number for display. Keep component scores visible so
readers can see why the final number is high or low.

## Component Scales

| Score | Meaning |
| --- | --- |
| 0-20 | Minimal concern |
| 21-40 | Some concern |
| 41-60 | Caution advised |
| 61-80 | High misinformation risk |
| 81-100 | Severe misinformation risk |

## Verdict-to-CFS Guide

- Confirmed: 0-10
- Mostly true: 10-25
- Mixed: 35-55
- Unverified: 45-65, depending on claim risk and source scarcity
- Misleading: 55-80
- False: 80-100

## MTS Guide

- 0-20: Neutral wording, no meaningful manipulation markers.
- 21-40: Some loaded framing but evidence remains inspectable.
- 41-60: Multiple medium red flags or one high red flag.
- 61-80: Strong emotional, conspiratorial, or statistical manipulation.
- 81-100: Coercive virality, dangerous claims, fabricated context, or coordinated
  manipulation markers.

## SCD Guide

- 0-20: Primary or independent Tier 1-4 sources, transparent authorship.
- 21-40: Mostly reliable sources with minor limitations.
- 41-60: Mixed source quality or limited independence.
- 61-80: Mostly Tier 7-8, opaque authorship, weak citations.
- 81-100: Anonymous, fabricated, imitation, or known unreliable source chain.

## Calibration Examples

- True official statistic shared neutrally: CFS 5, MTS 5, SCD 10, MFS 7.
- True quote stripped of important context: CFS 35, MTS 45, SCD 25, MFS 36.
- Unverified viral health claim from anonymous post: CFS 60, MTS 70, SCD 80, MFS 67.
- Fabricated election claim with urgent share language: CFS 90, MTS 85, SCD 85, MFS 88.

Always explain that the score summarizes risk factors in the analyzed content. It
does not replace the per-claim evidence.
