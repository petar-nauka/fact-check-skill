# Reference: Red-Flag Taxonomy

Load this when scanning content for manipulation markers (manipulation-scan step). Scan the
original content for the markers below. For each detected flag record: **Code** (e.g. A3, C6, F2),
**Label**, **Location** (quote the passage), **Severity** (see scale at the bottom), and a one-line
**Explanation**. This is the structure expected by `red_flags[]` in
`schema/fact_check_result.schema.json`. Red flags feed the **MTS** component of the MFS score
(see `mfs-calibration.md`).

Red flags are **not** proof that a claim is false — they are reasons to slow down and verify.
Keep the factual verdict evidence-led; use red flags to explain *how* the content is framed.

---

## Category A: Emotional Manipulation
- **A1** Inflammatory or fear-inducing language
- **A2** Appeal to outrage, disgust, or panic
- **A3** Urgent calls to action ("Share before they delete this!", "Wake up!")
- **A4** Us-vs-them / tribal framing
- **A5** Victimhood narrative (powerful group portrayed as persecuted)
- **A6** Moral panic ("Think of the children!")
- **A7** Disgust triggers (graphic content to override critical thinking)

## Category B: Source & Attribution Problems
- **B1** No author / anonymous
- **B2** No original source cited for key claims
- **B3** Fake or irrelevant expert credentials (authority in wrong field)
- **B4** Anonymous "insider" / "leaked" framing
- **B5** Source is a known disinformation outlet (check EUvsDisinfo)
- **B6** Source mimics a legitimate outlet (similar name/design)
- **B7** Circular sourcing (sources cite each other in a loop)
- **B8** Misattributed quotes or studies

## Category C: Logical Fallacies
- **C1** Cherry-picked data / statistics without context
- **C2** False dichotomy
- **C3** Straw man
- **C4** Appeal to irrelevant authority
- **C5** Hasty generalization from anecdotes
- **C6** Post hoc / false causation (correlation ≠ causation)
- **C7** Whataboutism / deflection
- **C8** Slippery slope without justification
- **C9** Moving the goalposts
- **C10** Burden-of-proof reversal ("Prove it's NOT true!")
- **C11** Naturalistic fallacy ("natural = good")
- **C12** Argument from incredulity

## Category D: Temporal & Contextual Manipulation
- **D1** Old content presented as new (recycled images/stats)
- **D2** Real facts in misleading context
- **D3** Selective editing/cropping (images, quotes, data)
- **D4** Headline contradicts the article body
- **D5** Translation manipulation (mistranslation / selective translation)
- **D6** Satire presented as real  *(see SKILL.md satire/opinion guard — may also mean this is NOT disinfo)*
- **D7** Real study misrepresented (conclusions exaggerated/inverted)

## Category E: Coordinated / Structural Signals
- **E1** Astroturfing (many identical/near-identical shares)
- **E2** Clickbait formatting (ALL CAPS, excessive punctuation, curiosity gaps)
- **E3** Deepfake / synthetic-media indicators
- **E4** Bot-like distribution (new accounts, no engagement)
- **E5** Cross-platform coordination (same narrative simultaneously)
- **E6** SEO manipulation (keyword stuffing, misleading meta)

## Category F: Health-Specific Manipulation (when claim is health-related)
- **F1** Miracle-cure claims
- **F2** VAERS/EudraVigilance misuse (reporting ≠ causation)
- **F3** Anti-institutional framing ("Doctors don't want you to know")
- **F4** Naturalistic health fallacy ("Big Pharma vs. natural remedies")
- **F5** Anecdotal healing stories as proof of efficacy
- **F6** Misrepresented or retracted studies cited as evidence
- **F7** Pseudoscientific terminology used to sound legitimate

---

## Severity Scale

Record `severity` as one of these strings (lowercase in the JSON result):

- **low** — framing issue that does not materially change the factual claim.
- **medium** — red flag affects interpretation, source trust, or context.
- **high** — red flag is central to the content's persuasive force.
- **critical** — red flag could cause health, safety, financial, or civic harm.

**Manipulation density:** roughly, the ratio of high+medium flags to content length. High density
signals more manipulative intent. Judge density relative to content length so long texts are not
penalized merely for containing more absolute flags. Severity and density inform the **MTS**
component only; the factual verdict stays evidence-led (see `mfs-calibration.md`).
