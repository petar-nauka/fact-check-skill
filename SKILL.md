---
name: fact-check
description: >
  Semi-automated fact-checking, disinformation detection, and media literacy skill.
  Use when a user asks to verify a claim, check if something is true, detect misinformation,
  fact-check an article or social media post, evaluate source reliability, compare two sources,
  or request a prebunking briefing. Trigger phrases: "is this true?", "is this fake?",
  "fact check this", "compare these sources", "проверка на факти", "истина ли е",
  "дезинформация ли е", "сравни тези източници", "какви фалшиви наративи има за X".
  Works with text, URLs, screenshots, and dual-source comparison. Produces HTML Fact-Check
  Cards with verdict, confidence, source scoring, red flags, origin tracing, educational tips,
  and share-safe summary. Multi-language source verification (BG, EN, RU).
---

# Fact-Check Skill v2.1

An advanced semi-automated fact-checking and disinformation detection system that produces
visual Fact-Check Cards. Combines the SIFT methodology (Stop, Investigate, Find, Trace),
the CRAAP test (Currency, Relevance, Authority, Accuracy, Purpose), prebunking/inoculation
science, and claim decomposition with multi-language source triangulation, manipulation
technique detection, origin tracing, counterfactual analysis, and a comprehensive
educational component.

Grounded in research: fact-check labels reduce belief in false claims by ~18% (Clayton et al.,
2020), accuracy prompts reduce sharing of false news by 15-20% (Pennycook & Rand, 2021), and
prebunking videos improve manipulation recognition by ~5% even after a single viewing
(van der Linden et al., 2022, Science Advances). This skill aims to maximize these effects
through structured, transparent, and educational analysis.

---

## Operating Modes

This skill operates in four modes depending on user intent:

### Mode 1: Standard Fact-Check (default)
User provides content (text, URL, or image) and asks for verification.
Runs the full 11-step pipeline. Produces a complete Fact-Check Card.

### Mode 2: Comparison Mode
User provides two sources/texts/URLs on the same topic and asks for comparison.
Runs decomposition on both, cross-references claims, identifies where they agree/disagree,
evaluates which is more credible and why. Produces a Comparison Fact-Check Card.

### Mode 3: Prebunking Briefing
User asks about current disinformation narratives on a topic (e.g., "What false narratives
are circulating about vaccines/elections/energy?"). Searches for active disinformation
campaigns on the topic, summarizes the most common false narratives, explains the
manipulation techniques used, and provides preemptive defense tips. Produces a
Prebunking Briefing Card.

### Mode 4: Quick Check
User asks a simple yes/no verification question (e.g., "Is it true that X?").
Runs an abbreviated pipeline (Steps 1, 2, 6, 7 only). Skip Steps 3-5 and 8-9.

**Quick Check output** (text response, not HTML card):
- Verdict badge (CONFIRMED / FALSE / etc.) with confidence level
- 1-2 sentence explanation
- Confidence calibration (brief: 1 line for increasing factors, 1 line for decreasing)
- 2-3 key sources with tier indicators
- One educational tip — pick using this priority: (1) the manipulation technique most
  visible in the claim's framing, (2) if no clear technique, use the domain-specific tip
  (health→F category, geopolitical→D category), (3) fallback to General Tip 4 (Source Triple-Check)
- Share-safe summary
- Disclaimer (same as Section 12 of the full card, shortened to 1 sentence)

**When to upgrade to full card:** If the user explicitly asks for HTML, a card, or
detailed analysis, OR if during the quick search you discover the claim is complex
(multiple sub-claims, mixed verdicts), upgrade to Mode 1 and run the full pipeline.
MFS scoring is NOT calculated for Quick Check — it requires red flag analysis (Step 5)
which Quick Check skips.

**Mode detection:** Infer the mode from the user's request. If ambiguous, default to
Mode 1. If the user provides two URLs or texts with comparative language ("compare",
"which is more reliable", "сравни"), use Mode 2. If the user asks about narratives
on a topic without specific content to check, use Mode 3.

---

## Input Processing

The user may provide content in these forms:

1. **Pasted text** -- a social media post, quote, claim, article excerpt, or message
2. **URL** -- use `web_fetch` to retrieve the content, then analyze
3. **Image/screenshot** -- read visible text from the image, then analyze
4. **Two sources** (Comparison Mode) -- two texts or URLs for side-by-side analysis
5. **Topic query** (Prebunking Mode) -- a topic name for narrative scanning

**Image-specific guidance:**
When the input is an image, after extracting text also note:
- Whether the image appears to be a screenshot of a social media post (note platform)
- Whether visible metadata (date, author, share count) is present
- Whether the image itself may be manipulated (visual artifacts, inconsistent lighting/shadows, text overlay style)
- Recommend reverse image search tools: Google Images, TinEye, Yandex Images
- If the image shows a person making a claim, note that the person's identity should be verified

**If the input is ambiguous or too vague**, ask the user ONE clarifying question before
proceeding. After decomposition (Step 1), briefly present the extracted claims and ask:
"Would you like me to check all of these, or focus on specific ones?" -- this saves time
and gives more relevant results. If the user does not respond or says "all", proceed with
all claims.

---

## Methodology -- The 11-Step Pipeline

### Step 1: Claim Decomposition

Break the input into individual **checkable units**. For each element in the text, classify it:

| Type | Code | Action |
|------|------|--------|
| **Factual claim** (verifiable) | F | Queue for checking |
| **Opinion / value judgment** | O | Mark as "Not checkable -- opinion" |
| **Prediction / future claim** | P | Mark as "Not checkable -- prediction" |
| **Vague / unfalsifiable** | U | Mark as "Not checkable -- unfalsifiable" |
| **Implied claim** (not stated directly but strongly suggested) | I | Extract the implied factual claim, queue for checking |
| **Statistical claim** (uses numbers, percentages, data) | S | Queue for checking with extra scrutiny on context |

Number each factual claim (C1, C2, C3...). This is the backbone of the analysis.

**Important:** Most disinformation is NOT 100% false -- it mixes truths with falsehoods.
A post may contain one true claim, one false claim, and two opinions. Showing
C1=Confirmed, C2=False, C3=Opinion, C4=Misleading is far more useful and honest
than a single binary verdict.

**For implied claims:** Disinformation often works through implication rather than direct
statement. "Exposed: the document THEY don't want you to see" implies (a) a conspiracy
to hide information and (b) that the document contains damaging truth. Extract these
implied claims explicitly.

**After decomposition, present the claims to the user** and ask if they want to focus
on specific ones or check all. Proceed after response (or proceed with all if no response).

**Skip the interactive checkpoint** in these cases:
- **Mode 4 (Quick Check):** Single claim, no need to ask.
- **Single-claim content:** Only one factual claim extracted — proceed directly.
- **Obvious disinformation:** Content has clear urgency markers (A3), anonymous source (B1),
  and/or viral social media framing — the user likely wants a full check, not a menu.
- **Non-interactive context:** Running as a batch/test, or on Claude.ai where the user
  expects a complete response in one turn.

### Step 2: Source Investigation (SIFT + CRAAP)

For each factual claim, perform **multi-language web searches**:

- Search in the **language of the original content**
- Search in **English** (for international coverage)
- If relevant, search in **Russian** (critical for Bulgarian disinformation landscape --
  many narratives originate from or are amplified by Russian-language sources)
- If relevant, search in **German, French, or other languages** (for EU policy, science,
  or geopolitical claims)

**Search strategy:**
- Use 3-5 short, specific queries per claim (different angles, different phrasings)
- Include at least one query formulated as the opposite of the claim (to find counterevidence)
- Search for the claim in quotes to find exact matches / viral spread patterns
- Search for the claim + "fact check" or "debunked" or "проверка"

**Source priority hierarchy (highest to lowest):**

| Tier | Source Type | Examples | Reliability |
|------|-----------|----------|-------------|
| 1 | Established fact-check organizations (IFCN-certified) | Snopes, PolitiFact, AFP Fact Check, Full Fact, FactCheck.org, EUvsDisinfo, Factcheck.bg, Detector.bg, AFP Proveri | Highest |
| 2 | Official institutional sources | WHO, CDC, EMA, ECDC, Eurostat, EUR-Lex, national statistical institutes, government agencies | Very High |
| 3 | Major wire services and quality journalism | Reuters, AP, BBC, DW, The Guardian, Dnevnik.bg, Capital.bg, Mediapool.bg | High |
| 4 | Peer-reviewed scientific publications | PubMed, Cochrane Reviews, Nature, The Lancet, Science, Google Scholar | Very High (for scientific claims) |
| 5 | Domain-specific expert organizations | IPCC (climate), IAEA (nuclear), ITU (tech), specialized NGOs | High |
| 6 | Other media with editorial standards | Regional newspapers, established online media | Medium |
| 7 | Blogs, personal sites, social media posts | Individual blogs, YouTube channels, Facebook posts | Low (use only as supplementary) |
| 8 | Anonymous or unattributable sources | No author, no organization, no verifiable origin | Very Low |

**Source scoring:** For each source used in the analysis, assign a reliability tier (1-8).
This will be displayed visually in the Fact-Check Card so readers can see at a glance
how strong the evidence base is.

**Triangulation rule:** Seek confirmation or refutation from at least **3 independent
sources from Tier 1-4**. If fewer than 3 such sources address the claim, explicitly note
this as a limitation and lower confidence accordingly.

**CRAAP evaluation for each key source:**
- **Currency:** When was it published? Is it up to date for the topic?
- **Relevance:** Does it directly address the claim?
- **Authority:** Who is the author/publisher? What are their credentials?
- **Accuracy:** Are claims supported by evidence? Are there citations?
- **Purpose:** Is the intent to inform, persuade, sell, or entertain?

### Step 3: Online Source Deep Evaluation (Lateral Reading Protocol)

For EVERY web source found during Step 2 -- both the sources the **original content
cites** and the sources **we find during verification** -- perform a structured
credibility evaluation. This step is critical: users must SEE the evaluation process
so they learn to do it themselves in the future.

**This step uses `web_search` and `web_fetch` actively.** For each key source:

#### 3a. Site-Level Credibility Audit

Fetch the source URL and evaluate the **website itself**:

| Question | What to look for | Red flag indicators |
|----------|-----------------|---------------------|
| **Who owns this site?** | Check "About Us", footer, domain WHOIS. Is there a named organization? | No about page, hidden ownership, recently registered domain |
| **What is the site's stated mission?** | Is it journalism, activism, commerce, satire? | Mission unclear; mix of news + product sales; no editorial policy |
| **Does it have editorial standards?** | Look for corrections policy, editorial board, code of ethics | No corrections page, no editorial board listed |
| **What do others say about this site?** | Search: `"sitename.com" reliability` or `"sitename" fact check`. Check Media Bias/Fact Check, Wikipedia, EUvsDisinfo | Flagged by multiple fact-checkers; Wikipedia "unreliable source" tag |
| **What is the domain pattern?** | Legitimate domains vs. imitation domains (e.g., bbc-news24.com vs. bbc.com) | Domain mimics known outlet; excessive hyphens; unusual TLD |
| **Is there advertising?** | Some ads are normal; wall-to-wall clickbait ads suggest revenue-driven content | Aggressive ad placement; "miracle cure" or casino ads; pop-ups |
| **Does the site disclose funding?** | Quality outlets disclose ownership and funding | Funding completely opaque; state-funded without disclosure |

**Output per site: Site Credibility Rating**
- **Established & Transparent** (named org, editorial standards, corrections policy, known history)
- **Credible but Limited** (real organization but small, niche, or limited track record)
- **Questionable** (lacks transparency, flagged by fact-checkers, or unclear mission)
- **Unreliable** (known disinformation outlet, no identifiable owner, fake domain)
- **Cannot Assess** (paywalled, minimal public information about the outlet)

#### 3b. Author-Level Credibility Check

For each article or source used, evaluate the **author**:

| Question | What to look for | Red flag indicators |
|----------|-----------------|---------------------|
| **Is an author named?** | Real name, byline, bio | No author; "Staff", "Admin", or pseudonym only |
| **What are their credentials?** | Relevant education, professional experience, publication history | No verifiable credentials; credentials in unrelated field |
| **Do they have a track record?** | Search their name + topic. Have they published elsewhere? | No other publications; only appears on this one site |
| **Are they a real person?** | Social media presence, LinkedIn, university affiliation | No trace online; stock photo avatar; AI-generated profile photo |
| **Domain expertise match?** | Is their expertise in the field they're writing about? | Writing about medicine without medical background; physicist on vaccines |

**When no author is identifiable:** This is a B1 red flag (already in Step 5) but here
we escalate: an unattributed source making strong claims about health, politics, or
science is automatically scored as Tier 7-8 regardless of site appearance.

#### 3c. Evidence & Citation Evaluation

For each source, evaluate the **quality of evidence it provides**:

| Question | What to look for | Red flag indicators |
|----------|-----------------|---------------------|
| **Does it cite primary sources?** | Links to studies, documents, official data | No citations; "research shows" without specifying which research |
| **Are citations real and accurate?** | Click through to cited sources. Do they say what the article claims? | Broken links; cited source says the opposite; citation is to another blog |
| **What type of evidence is used?** | Peer-reviewed studies > institutional reports > expert quotes > anecdotes | Only anecdotes; only quotes from one "expert"; no data |
| **Is the data presented in context?** | Absolute numbers + rates, time periods, comparisons, methodology | Percentages without base numbers; no time frame; cherry-picked data range |
| **Is there a clear methodology?** | For studies: sample size, controls, peer review status | No methodology; tiny sample; unpublished; preprint presented as final |
| **Are counterarguments addressed?** | Balanced reporting includes opposing views or limitations | Only one side presented; opposing views dismissed or straw-manned |

**Evidence Quality Rating per source:**
- **Strong** -- Cites peer-reviewed research, official data, or multiple expert sources; evidence directly supports the claims made
- **Moderate** -- Some citations present but incomplete; relies partly on expert opinion without primary data
- **Weak** -- Few or no citations; relies on anecdotes, unnamed sources, or other non-primary material
- **Fabricated/Misrepresented** -- Citations exist but are fake, broken, misquoted, or say the opposite of what's claimed

#### 3d. Cross-Reference Check (Lateral Reading)

This is the core of the **lateral reading method** (Stanford Civic Online Reasoning):

Instead of reading a source deeply to judge it from within, **leave the page** and
search for what independent, reliable sources say about:
1. The specific claim being made
2. The author making it
3. The website publishing it

**Procedure:**
1. Open a new search for the core claim in different words
2. Search for the author's name + "controversy" or "credibility"
3. Search for the website name + "reliability" or "fact check"
4. Check if the claim appears in Tier 1-3 sources. If it ONLY appears in Tier 7-8
   sources, that is itself a significant finding.

**Key principle to communicate to users:** Professional fact-checkers spend LESS time
reading the source itself and MORE time checking what others say about it. This is
counterintuitive but far more effective. A slick, professional-looking website can
be completely fabricated. But if Media Bias/Fact Check, Wikipedia, and multiple
independent journalists all flag it as unreliable, that consensus is meaningful.

#### 3e. Source Evaluation Summary Table

For each key source evaluated, produce a compact summary:

```
Source: [URL or name]
Site Rating: [Established / Credible / Questionable / Unreliable / Cannot Assess]
Author: [Name or "Unidentified"] -- Credentials: [relevant / irrelevant / unverifiable]
Evidence Quality: [Strong / Moderate / Weak / Fabricated]
Tier Assignment: [1-8]
Lateral Check: [What independent sources say about this site/author]
Key Finding: [1-sentence summary of what this source contributes or why it's problematic]
```

This table is displayed in the Fact-Check Card (Section 9: Sources Used) so the user
can see exactly WHY each source was rated as it was.

**CRITICAL FOR EDUCATIONAL IMPACT:** The purpose of this step is NOT just to evaluate
sources for our analysis. It is to **demonstrate the evaluation process** so that users
learn to replicate it independently. Every evaluation should be written as if teaching
the reader: "Here is how you check whether a source is trustworthy."

### Step 4: Origin Tracing

For each major claim, attempt to trace its origin:

1. **First appearance:** When and where did this claim first appear online?
   Search for the earliest instances using date-restricted searches.
2. **Original language:** Was the claim originally in a different language?
   This is critical for the Bulgarian context where many narratives are translated
   from Russian (RT, Sputnik, Tsargrad) or adapted from English conspiracy ecosystems.
3. **Mutation tracking:** How has the claim changed as it spread? Common mutations:
   - Numbers get inflated (100 becomes 1000 becomes "millions")
   - Hedging disappears ("may cause" becomes "causes")
   - Context is stripped (a quote loses its qualifiers)
   - Geographic/temporal shift (old event presented as current, foreign event presented as local)
4. **Known campaign association:** Does this claim match patterns from known disinformation
   campaigns documented by EUvsDisinfo, Hamilton 2.0, or similar trackers?

**Output:** A brief origin summary: "This claim appears to have originated from [source]
in [language] on approximately [date]. It has been adapted/translated and spread through
[channels]. [Notable mutations if any]."

If origin cannot be determined, state this explicitly.

### Step 5: Red Flag Detection

Scan the original content for manipulation markers. Check against this expanded taxonomy:

**Category A: Emotional Manipulation**
- A1: Inflammatory or fear-inducing language
- A2: Appeal to outrage, disgust, or panic
- A3: Urgent calls to action ("Share before they delete this!", "Wake up!")
- A4: Us-vs-them framing / tribal language
- A5: Victimhood narrative (portraying a powerful group as persecuted)
- A6: Moral panic framing ("Think of the children!")
- A7: Disgust triggers (graphic descriptions meant to override critical thinking)

**Category B: Source & Attribution Problems**
- B1: No author identified / anonymous
- B2: No original source cited for key claims
- B3: Fake or irrelevant expert credentials (authority in wrong field)
- B4: Anonymous "insider" or "leaked" framing
- B5: Source is a known disinformation outlet (check EUvsDisinfo database)
- B6: Source mimics legitimate outlet (similar name/design to trusted media)
- B7: Circular sourcing (sources cite each other in a loop)
- B8: Misattributed quotes or studies

**Category C: Logical Fallacies**
- C1: Cherry-picked data / statistics without context
- C2: False dichotomy (only two options presented)
- C3: Straw man (misrepresenting the opposing view)
- C4: Appeal to irrelevant authority
- C5: Hasty generalization from anecdotes ("My neighbor took X and got sick, so X is dangerous")
- C6: Post hoc ergo propter hoc (false causation / correlation vs. causation confusion)
- C7: Whataboutism / deflection
- C8: Slippery slope without justification
- C9: Moving the goalposts (shifting the claim when challenged)
- C10: Burden of proof reversal ("Prove it's NOT true!")
- C11: Naturalistic fallacy ("Natural = good, artificial = bad")
- C12: Argument from incredulity ("I can't understand how X works, so X must be false")

**Category D: Temporal & Contextual Manipulation**
- D1: Old content presented as new (recycled images, outdated statistics)
- D2: Real facts placed in misleading context
- D3: Selective editing or cropping (of images, quotes, or data)
- D4: Headline contradicts the article body
- D5: Translation manipulation (mistranslation or selective translation)
- D6: Satirical content presented as real
- D7: Real study misrepresented (conclusions exaggerated or inverted)

**Category E: Coordinated / Structural Signals**
- E1: Astroturfing patterns (many identical or near-identical shares)
- E2: Clickbait formatting (ALL CAPS, excessive punctuation, curiosity gaps)
- E3: Deepfake / synthetic media indicators (for images/video if applicable)
- E4: Bot-like distribution (many shares from new accounts, no engagement)
- E5: Cross-platform coordination (same narrative appearing simultaneously across platforms)
- E6: SEO manipulation (keyword stuffing, misleading meta descriptions)

**Category F: Health-Specific Manipulation** (when claim is health-related)
- F1: Miracle cure claims ("X cures cancer/diabetes/everything")
- F2: VAERS/EudraVigilance data misuse (reporting ≠ causation)
- F3: Anti-institutional framing ("Doctors don't want you to know")
- F4: Naturalistic health fallacy ("Big Pharma vs. natural remedies")
- F5: Anecdotal healing stories as proof of efficacy
- F6: Misrepresented or retracted studies cited as evidence
- F7: Pseudoscientific terminology used to sound legitimate

For each detected red flag, record:
- **Code** (e.g., A3, C6, F2)
- **Location** in the text (quote the relevant passage)
- **Severity:** Minor (stylistic, may be unintentional) / Moderate (likely intentional,
  affects interpretation) / Serious (clear manipulation, fundamentally distorts the message)

**Manipulation density score:** Calculate the ratio of serious+moderate flags to total
content length. High density = more manipulative intent.

### Step 6: Verdict Assignment + Severity Scoring

For each factual claim, assign a verdict on this 6-point scale:

| Verdict | Color Code | Verdict Points (VP) | Meaning |
|---------|-----------|---------------------|---------|
| CONFIRMED | #16a34a (Green) | 0 | Supported by multiple reliable Tier 1-4 sources |
| MOSTLY TRUE | #65a30d (Lime) | 1 | Core claim is accurate; minor details imprecise or unverifiable |
| MIXED | #ca8a04 (Yellow) | 3 | Contains both true and false elements in significant proportion |
| UNVERIFIED | #ea580c (Orange) | 4 | Cannot be confirmed or denied with available evidence |
| MISLEADING | #dc2626 (Red-Orange) | 7 | Contains factual elements but presented in a way that leads to false conclusions |
| FALSE | #991b1b (Dark Red) | 10 | Directly contradicted by reliable evidence |

**Confidence level** for each verdict: High / Medium / Low

#### Severity Score Algorithm

Calculate a numeric **Manipulation & Falsehood Score (MFS)** from 0 to 100 for the
overall content. This gives a repeatable, transparent number alongside the qualitative verdict.

**Component 1: Claim Falsehood Score (CFS)** -- weight 50%
```
CFS = (Sum of VP for all factual claims) / (Max possible VP) * 100
where Max possible VP = number_of_factual_claims * 10
```
Example: 4 claims -- CONFIRMED(0) + FALSE(10) + MIXED(3) + MISLEADING(7) = 20 / 40 = 50

**Component 2: Manipulation Technique Score (MTS)** -- weight 30%
```
For each red flag detected:
  - Serious severity: 8 points
  - Moderate severity: 4 points
  - Minor severity: 1 point

MTS = min(100, total_flag_points / expected_max * 100)
where expected_max = max(8, 3 * (number_of_sentences_in_content / 5))
```
The denominator scales with content length so that longer texts are not penalized
just for having more absolute flags. The `max(8, ...)` floor prevents extreme scores
on very short content (e.g., a 2-sentence social media post with 2 flags should not
auto-score 100%). Cap at 100.

**Component 3: Source Credibility Deficit (SCD)** -- weight 20%
```
For each source the original content relies on (not our verification sources):
  - Tier 1-2: 0 penalty points
  - Tier 3-4: 1 penalty point
  - Tier 5-6: 3 penalty points
  - Tier 7:   6 penalty points
  - Tier 8:   10 penalty points
  - No source cited at all: 10 penalty points

SCD = (Sum of penalty points) / (number_of_claims * 10) * 100, capped at 100

where number_of_claims = only claims classified as F (Factual) or S (Statistical)
in Step 1. Do NOT count Opinion (O), Prediction (P), Unfalsifiable (U), or
Implied (I) claims — these don't have independent source requirements.
```

**Final MFS calculation:**
```
MFS = (CFS * 0.50) + (MTS * 0.30) + (SCD * 0.20)
```

**Interpretation scale displayed in the card:**

| MFS Range | Label | Color | Meaning |
|-----------|-------|-------|---------|
| 0-10 | Reliable | Green | Content is well-sourced and factually sound |
| 11-25 | Mostly Reliable | Lime | Minor issues; broadly trustworthy |
| 26-45 | Caution Advised | Yellow | Notable problems; verify key claims independently |
| 46-65 | Problematic | Orange | Significant falsehoods or manipulation; do not share |
| 66-85 | Highly Misleading | Red | Majority false/manipulative; likely intentional disinfo |
| 86-100 | Disinformation | Dark Red | Pervasive falsehood + manipulation; clear disinfo pattern |

Always show the breakdown (CFS/MTS/SCD) alongside the final score so the user
can see WHERE the problem lies: is it the facts? the rhetoric? the sources?

**Overall verdict** for the entire piece of content is derived from a combination of:
- The MFS score (primary signal)
- Number and severity of false/misleading claims vs. confirmed claims
- Presence and severity of manipulation techniques
- Overall framing and apparent intent
- Whether the piece has a clear disinformation pattern or appears to be honest error

The MFS score is a tool for transparency, not a replacement for judgment. If the
numeric score and qualitative assessment diverge, explain why (e.g., "The MFS is 35
but the overall verdict is MISLEADING because the single false claim is the central
thesis of the article, while the confirmed claims are trivial context").

### Step 7: Confidence Calibration

For each verdict, provide a transparent explanation of WHY the confidence level is
what it is. Structure:

```
Confidence: [High/Medium/Low]
Factors increasing confidence:
- [e.g., "4 independent Tier 1-2 sources agree on the refutation"]
- [e.g., "Official data directly contradicts the claim with specific numbers"]
Factors decreasing confidence:
- [e.g., "All sources are from the same geographic region"]
- [e.g., "No peer-reviewed study directly addresses this specific claim"]
- [e.g., "The claim is very recent and fact-checkers may not have covered it yet"]
```

This transparency is critical. Research (Warren et al., CHI 2025) shows that
fact-checkers and users want to see "the work", not just the result. Showing the
reasoning builds trust and teaches the user how to evaluate evidence themselves.

### Step 8: Chain of Reasoning

For each claim with a non-obvious verdict (anything other than clearly Confirmed or
clearly False), provide a step-by-step reasoning chain:

```
Claim: [the claim]
Step 1: [What we searched for]
Step 2: [What we found -- key evidence for and against]
Step 3: [How we weighed conflicting evidence, if any]
Step 4: [Why we arrived at this specific verdict]
Conclusion: [Verdict] because [1-2 sentence summary]
```

This makes the analysis auditable and educational. The user can disagree with specific
steps rather than just accepting or rejecting the whole conclusion.

### Step 9: Counterfactual Analysis ("What Would Make This True?")

For each claim rated MISLEADING, UNVERIFIED, or FALSE, add a counterfactual section:

"If this claim were true, we would expect to find:
- [Specific evidence that should exist but doesn't]
- [Specific records/documents that should be available]
- [Specific institutional responses that should have occurred]

None of these exist / Only partial evidence exists / The evidence points in
the opposite direction."

**Example:** "If the EU were truly planning this law, we would expect to find:
a record in EUR-Lex, a press release from the European Commission, media reports
from accredited Brussels correspondents. None of these exist."

This teaches users what to look for when evaluating claims independently and is
one of the most effective educational techniques for building long-term critical
thinking skills.

### Step 10: Educational Component (Teach the User to Fish)

This is not a supplementary section. This is the most important long-term output
of the skill. The goal: after reading several Fact-Check Cards, the user should be
able to independently evaluate information without needing this tool.

Research basis: Prebunking (inoculation) is more effective than debunking because
it builds resistance BEFORE exposure (van der Linden et al., 2022). The Stanford
Civic Online Reasoning project (2023) showed that lateral reading -- checking
sources via external search rather than evaluating from within -- is the single
most effective technique used by professional fact-checkers and can be taught to
non-experts with immediate results.

Generate the educational section with ALL of these sub-sections:

#### 10a. Manipulation Technique Recognition

For EACH red flag detected in Step 5, provide a structured mini-lesson:

```
TECHNIQUE DETECTED: [Plain-language name, e.g., "Appeal to Fear"]
Red Flag Code: [e.g., A1]

WHAT HAPPENED IN THIS CONTENT:
[Quote the specific passage and explain exactly how this technique was used here.
Be concrete -- reference the actual text, not abstract descriptions.]

HOW TO RECOGNIZE THIS IN THE WILD:
[Give 2-3 common patterns/templates this technique uses. Examples:
- "Share before they delete this!" (urgency + censorship framing)
- "What they don't want you to know..." (exclusivity + conspiracy)
- "EXPOSED: The truth about..." (revelation framing + emotional charge)]

WHY YOUR BRAIN FALLS FOR IT:
[Name the specific cognitive bias exploited and explain the mechanism in 2-3
sentences. Reference: confirmation bias, availability heuristic, authority bias,
halo effect, continued influence effect, illusory truth effect, anchoring bias,
bandwagon effect, Dunning-Kruger effect, as relevant.]

YOUR DEFENSE:
[One concrete, actionable self-defense tip the reader can apply immediately.
Frame as a personal habit to build, not a rule to follow.]
```

Prioritize the 5 most common manipulation categories the user is likely to
encounter in everyday browsing:
1. **Emotional appeals** (fear, outrage, urgency, moral panic)
2. **Fake/irrelevant expert authority** (wrong-field credentials, anonymous sources)
3. **Cherry-picked data** (statistics without context, percentages without baselines)
4. **Clickbait and curiosity gaps** (sensational headlines, teaser framing)
5. **Conspiratorial logic** (unfalsifiable claims, censorship narratives, "just asking questions")

#### 10b. Lateral Reading -- Teaching the Method

Present the lateral reading method explicitly as a learnable skill:

```
HOW PROFESSIONAL FACT-CHECKERS ACTUALLY WORK:
(Based on Stanford Civic Online Reasoning, 2023)

The counterintuitive finding: Professional fact-checkers spend LESS time
reading the source itself and MORE time checking what OTHERS say about it.
Amateurs do the opposite -- they read deeply within a source to judge it.
This is less effective because a well-designed disinformation site can look
perfectly credible from the inside.

THE LATERAL READING METHOD -- 4 STEPS:

Step 1: STOP
Do not read the article deeply. Instead, note the claim and the source.

Step 2: LEAVE THE PAGE
Open a new browser tab. Search for information ABOUT the source:
- "[site name] reliability"
- "[site name] fact check"
- "[author name] credentials"
- "[author name] controversy"

Step 3: CHECK WHAT INDEPENDENT SOURCES SAY
Look for assessments from:
- Wikipedia (check if the source has a "reliability" or "bias" note)
- Media Bias/Fact Check (mediabiasfactcheck.com)
- EUvsDisinfo (for EU/Eastern European sources)
- Fact-checking organizations (Snopes, PolitiFact, Factcheck.bg)

Step 4: FIND BETTER COVERAGE
Search for the CLAIM (not the article) in different words.
If reputable sources (Reuters, AP, BBC, institutional sources) cover it,
read their version. If NO reputable source covers it, that is itself
a significant finding.

KEY INSIGHT: You don't need expertise in the topic to evaluate a source.
You just need to check what people who DO have expertise say about it.
```

**CRITICAL:** In this specific analysis, show the user exactly how lateral
reading was applied. Example: "When we checked [source name], we found that
Media Bias/Fact Check rates it as [rating]. Wikipedia describes it as [description].
This is how lateral reading works in practice -- we didn't just read the article,
we checked what others say about the outlet."

#### 10c. Source Credibility Lesson

Based on the sources evaluated in Step 3, teach the user the practical
source evaluation questions they should ask for ANY content they encounter:

```
THE 5 QUESTIONS TO ASK ABOUT ANY SOURCE:

1. WHO is behind this? (Named organization? Individual? Anonymous?)
2. WHAT is their track record? (Do fact-checkers flag them? What does Wikipedia say?)
3. DO they cite evidence? (Links to primary sources? Named experts? Specific data?)
4. WHO ELSE is reporting this? (Is it ONLY on this site, or do reputable outlets cover it?)
5. WHAT is the purpose? (To inform? To persuade? To sell? To generate outrage/clicks?)

If any answer is "I don't know" or "I can't find out," treat the claim
with proportional skepticism.
```

#### 10d. Known Narrative Alert

If this claim matches a documented recurring disinformation narrative
(especially in the Bulgarian context), provide a narrative card:

```
KNOWN NARRATIVE ALERT:
This claim matches a documented disinformation pattern.

Narrative: [Name/description of the recurring narrative]
Active since: approximately [year]
Previous versions: [Brief description of how the narrative has evolved]
Part of broader pattern: [Narrative type -- e.g., pro-Kremlin, anti-vaccine,
  EU skepticism, health misinformation]
Documented by: [Which organizations have tracked this -- EUvsDisinfo,
  Factcheck.bg, etc.]
```

#### 10e. Prebunking Vaccine

Based on inoculation theory (van der Linden et al., 2022, Science Advances),
provide a "psychological vaccine" -- a brief, memorable explanation of how
the specific manipulation technique works, designed to build resistance
against future encounters regardless of the specific topic:

```
INOCULATION (so you recognize this next time):
The technique used here is called [name].
It works by [1-sentence mechanism].
Next time you encounter it, you'll notice [specific pattern to watch for].
Remember: [one memorable takeaway sentence].
```

The prebunking tip should be SHORT (4-5 sentences max), MEMORABLE, and
GENERALIZABLE -- it should help the user recognize this technique in any
future context, not just on this specific topic.

#### 10f. Domain-Specific Guidance

If the content is health-related, add:
- How to check health claims (PubMed, Cochrane, WHO)
- VAERS/EudraVigilance data: reporting ≠ causation
- Peer-reviewed studies vs. preprints vs. blog posts
- The difference between "a study found" and "the scientific consensus is"

If the content is geopolitical/political:
- How to check legislative claims (EUR-Lex, official government sites)
- How to identify state-sponsored media (RT, Sputnik, CGTN)
- How to distinguish between editorials/opinions and news reporting

Read `educational-tips.md` for the full tip database. If the file is not available,
generate tips from knowledge of media literacy, cognitive psychology, and the
research literature on disinformation.

### Step 11: Output Generation

Generate the Fact-Check Card and a share-safe summary.

---

## Output: The Fact-Check Card

Generate an **HTML artifact** (single .html file).

The card MUST include these sections:

### 1. Header
- Title: "Fact-Check Card" / "Карта за проверка на факти" (match user language)
- Date of analysis
- Analysis mode badge (Standard / Comparison / Prebunking / Quick)

### 2. Original Content Summary
- Brief summary of what was checked (2-3 sentences max)
- Source of the content if known (platform, author, date)

### 3. Overall Verdict + MFS Score
- Large, color-coded badge with verdict text
- Confidence level with visual indicator
- **MFS Score gauge:** Visual 0-100 gauge with color zones (green→red)
  - Show the final MFS number prominently
  - Below the gauge, show the 3-component breakdown:
    - CFS (Claim Falsehood): [score]/100 -- weight 50%
    - MTS (Manipulation Techniques): [score]/100 -- weight 30%
    - SCD (Source Credibility Deficit): [score]/100 -- weight 20%
  - Color the MFS label according to the interpretation scale (Reliable → Disinformation)
  - Brief 1-sentence interpretation (e.g., "Caution Advised -- notable problems detected")

### 4. Confidence Calibration
- Compact display of factors increasing/decreasing confidence

### 5. Claims Breakdown
- Each claim (C1, C2...) with:
  - The claim text
  - Classification badge (Factual / Opinion / Prediction / Unfalsifiable / Implied)
  - Individual verdict badge (color-coded)
  - Mini chain of reasoning (collapsed by default, expandable)
  - Key sources for this specific claim (with tier indicators)

### 6. Counterfactual Section (for FALSE/MISLEADING claims)
- "What would make this true?" analysis

### 7. Red Flags Detected
- Visual list with category icons, severity indicators (color-coded dots)
- Brief explanation of each flag

### 8. Origin Trace (if applicable)
- Timeline or brief narrative of where the claim originated and how it spread
- Language of origin if different from the analyzed content

### 9. Sources Used (with Evaluation)
- Numbered list of sources with:
  - Tier indicator (visual badge: T1, T2, etc.)
  - Source name and link (where available)
  - **Site credibility rating** (from Step 3a evaluation)
  - **Author credentials** (from Step 3b evaluation)
  - **Evidence quality** (from Step 3c evaluation)
  - Brief note on what this source contributed to the analysis
- For each source, include the lateral reading finding (what independent sources
  say about this site/author) -- this transparency teaches users the evaluation method
- Collapsible "How we evaluated this source" detail for each entry

### 10. Educational Section
- **10a: Manipulation Technique Recognition** -- Structured mini-lessons for each
  detected technique (what happened, how to recognize it, why it works, your defense)
- **10b: Lateral Reading Method** -- The 4-step protocol with specific examples from
  this analysis showing how it was applied
- **10c: Source Credibility Lesson** -- The 5 questions to ask about any source
- **10d: Known Narrative Alert** (if applicable) -- Documented disinfo pattern match
- **10e: Prebunking Vaccine** -- Inoculation tip for future encounters
- **10f: Domain-Specific Guidance** (if applicable) -- Health or geopolitical tips

### 11. Share-Safe Summary
- A pre-written, copy-ready text (2-3 sentences) that the user can paste into
  a comment or message to respond to someone who shared the original content.
- Requirements for this text:
  - Neutral, respectful tone (no aggression, no condescension)
  - States the verdict clearly
  - Gives the key reason
  - Includes a link to a fact-check source (if one exists)
  - Constructive framing ("This claim has been verified and found to be [verdict].
    Here's why: [brief reason]. More information: [link]")

### 12. Disclaimer
- "This is an AI-assisted analysis, not a definitive fact-check. For critical decisions,
  consult professional fact-checkers and primary sources. AI analysis may contain errors --
  always verify key findings independently."

### Design Requirements for HTML:
- Self-contained single file (inline CSS, no external dependencies)
- Clean, professional design with clear visual hierarchy and 8px spacing system
- Color-coded verdict badges (green-to-red scale as defined in Step 6)
- Source tier badges with distinct visual styling
- Collapsible sections for chain of reasoning (use `<details>/<summary>` HTML elements)
- Mobile-friendly (responsive, readable on 320px+ screens)
- Dark/light theme support via `prefers-color-scheme` media query
- Print-friendly layout via `@media print`
- Language: Match the language of the user's request
- Typography: System font stack for maximum compatibility
- Maximum 3 font weights (regular, medium, bold)
- Sufficient contrast ratios for all text (WCAG AA minimum)
- No purple/indigo/violet hues -- use a professional palette based on
  the verdict color scale (greens, yellows, oranges, reds) with neutral grays

**Required CSS variables** (use these exact values for consistency across all cards):
```css
:root {
  --bg: #ffffff;
  --bg-secondary: #f8f9fa;
  --bg-tertiary: #f1f3f5;
  --text: #1a1a1a;
  --text-secondary: #495057;
  --text-tertiary: #868e96;
  --border: #dee2e6;
  --border-light: #e9ecef;
  --green: #16a34a;      /* CONFIRMED */
  --lime: #65a30d;       /* MOSTLY TRUE */
  --yellow: #ca8a04;     /* MIXED */
  --orange: #ea580c;     /* UNVERIFIED */
  --red-orange: #dc2626; /* MISLEADING */
  --dark-red: #991b1b;   /* FALSE */
  --shadow: 0 1px 3px rgba(0,0,0,0.08);
  --shadow-md: 0 4px 12px rgba(0,0,0,0.1);
  --radius: 8px;
  --radius-sm: 4px;
}

@media (prefers-color-scheme: dark) {
  :root {
    --bg: #1a1a2e;
    --bg-secondary: #16213e;
    --bg-tertiary: #0f3460;
    --text: #e8e8e8;
    --text-secondary: #b0b0b0;
    --text-tertiary: #808080;
    --border: #2a2a4a;
    --border-light: #222244;
    --shadow: 0 1px 3px rgba(0,0,0,0.3);
    --shadow-md: 0 4px 12px rgba(0,0,0,0.4);
  }
}
```

**Required badge classes:**
```css
.badge-confirmed { background: var(--green); color: #fff; }
.badge-mostly-true { background: var(--lime); color: #fff; }
.badge-mixed { background: var(--yellow); color: #fff; }
.badge-unverified { background: var(--orange); color: #fff; }
.badge-misleading { background: var(--red-orange); color: #fff; }
.badge-false { background: var(--dark-red); color: #fff; }
```

**Required tier badge classes:**
```css
.tier-1, .tier-2 { background: #dcfce7; color: #166534; }
.tier-3, .tier-4 { background: #dbeafe; color: #1e40af; }
.tier-5, .tier-6 { background: #fef9c3; color: #854d0e; }
.tier-7, .tier-8 { background: #fecaca; color: #991b1b; }
```

All cards MUST use these exact CSS variables and badge classes to ensure visual consistency.
The container should use `max-width: 800px; margin: 0 auto;` and body font should be
the system font stack: `-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif`.

---

## Comparison Mode (Mode 2) Specifics

When comparing two sources:

1. Run Step 1 (decomposition) on both sources independently
2. Cross-reference claims:
   - **Agreed facts:** Claims present in both sources with same meaning
   - **Contradictions:** Claims where the two sources directly disagree
   - **Exclusive claims:** Claims present in only one source
3. For contradictions, investigate which source is more reliable using Steps 2-5
4. Produce a Comparison Card with:
   - Side-by-side claim breakdown
   - Agreement/disagreement matrix
   - Per-source credibility assessment (based on source tier, red flags, evidence quality)
   - Overall assessment: which source is more reliable and why

---

## Prebunking Briefing Mode (Mode 3) Specifics

Mode 3 does NOT use the 11-step pipeline. It has its own workflow:

**Pipeline for Mode 3:** Search → Document → Educate → Output

**Step M3-1: Narrative Search**
Search for current disinformation narratives on the given topic using:
- `web_search` for: "[topic] disinformation", "[topic] fact check", "[topic] EUvsDisinfo"
- EUvsDisinfo database (search via web)
- Recent fact-check articles from Tier 1 organizations
- News reports about disinformation campaigns
- Google Fact Check Explorer (search via web)
Search in multiple languages (BG, EN, RU as relevant).

**Step M3-2: Narrative Documentation**
For each active narrative found (aim for 3-7), document:
- The core false claim (quote or paraphrase)
- The manipulation technique(s) used (use red flag codes from Step 5 taxonomy)
- Spread level based on search evidence:
  - **High** — appears in 10+ search results, covered by multiple fact-checkers, cross-platform
  - **Medium** — appears in 3-9 search results, or covered by 1-2 fact-checkers
  - **Low** — fewer than 3 search results, niche or emerging narrative
- The factual counter-evidence (with sources and tier indicators)

**Step M3-3: Educational Component**
Generate these educational sections (from Step 10):
- **10a** — deduplicate techniques across all narratives first, then generate ONE mini-lesson
  per unique technique. Consolidate to the 5 most impactful (most frequently appearing or
  most dangerous). Example: if A1 appears in 4 narratives, it gets 1 mini-lesson, not 4.
- **10b** — lateral reading method (always include)
- **10c** — source credibility lesson (always include)
- **10d** — only for narratives that match *previously documented recurring patterns* (i.e.,
  narratives tracked by EUvsDisinfo, Factcheck.bg, or similar). Do NOT repeat the M3-2
  documentation — 10d adds the meta-level tracking (active since, previous versions, part
  of broader pattern). If a narrative is new/undocumented, skip 10d for it.
- **10e** — deduplicate same as 10a: one prebunking vaccine per unique technique, max 5
- **10f** — domain-specific guidance (always include, matched to topic)

**Step M3-4: Output — Prebunking Briefing Card (HTML)**
Produce an HTML card with:
- Topic header with "Prebunking Briefing" mode badge
- List of active false narratives with spread indicators
- For each: the claim, the technique (with red flag code), the truth, and a defense tip
- Full educational section (10a-10f as specified above)
- General "inoculation" advice for this topic area
- Key reliable sources for accurate information on this topic
- Disclaimer

MFS scoring is NOT calculated for Mode 3 — there is no single content piece to score.

---

## Important Guidelines

### Epistemic Honesty
- When evidence is insufficient, say so clearly. "Unverified" is a valid and valuable verdict.
- Never manufacture confidence. If sources conflict, present the conflict.
- Distinguish between "no evidence found" and "evidence found that contradicts."
- Be transparent about limitations: paywalled content, recency of claims, language barriers.
- If a claim is on a topic where scientific consensus is still forming, note this explicitly.
- Never dismiss a claim solely because it contradicts mainstream narratives -- evaluate the
  evidence. But note when a claim contradicts strong scientific consensus (e.g., climate change,
  vaccine safety, evolution).

### Bias Awareness
- Search for sources on multiple sides of contested issues.
- Note when a claim is on a politically charged topic and extra caution is warranted.
- Do not let the framing of the original text bias the search queries.
- Present fact-check organization ratings where available, noting their methodology.
- Be aware of your own potential biases as an AI system -- flag when a topic is at the
  boundary of your knowledge or when your training data may not reflect the latest evidence.

### Bulgarian Context Awareness
- 46% of young Bulgarians cannot distinguish fact from opinion online (AEJ-Bulgaria, 2023).
- Many disinformation narratives in Bulgaria are translated/adapted from Russian sources.
- Key local disinformation themes: pro-Kremlin geopolitical narratives, health misinformation
  (anti-vaccine, miracle cures), EU/NATO skepticism, energy policy disinformation,
  historical revisionism (Bulgarian-Macedonian, Bulgarian-Turkish relations),
  election manipulation.
- Known low-credibility Bulgarian outlets exist (be aware but do not create a blocklist --
  evaluate each claim on its merits).
- Local fact-checking resources: Factcheck.bg, AFP Proveri, Detector.bg, Mediapool.bg.

### Health Claims -- Special Protocol
When a claim is health-related, apply additional scrutiny:
- Check if the claim involves VAERS/EudraVigilance data: these are reporting systems,
  not proof of causation. Reports in these systems mean "this happened after vaccination"
  NOT "vaccination caused this." Always clarify this distinction.
- Check Cochrane Reviews and PubMed for systematic evidence.
- Note the difference between peer-reviewed studies, preprints, and blog posts.
- For claims about "natural remedies" or "alternative medicine": check whether the
  substance has been tested in randomized controlled trials.
- WHO, EMA, CDC, and national health authorities are authoritative for health guidance.
- Flag any claim that could lead to dangerous health decisions (refusing treatment,
  self-medicating, delaying medical care) with a prominent health safety notice.

### Handling Blocked, Paywalled, or Inaccessible Sources
When `web_fetch` fails (HTTP 402/403/429, timeout, CAPTCHA, etc.):
1. **Do not silently skip the source.** Note the failure explicitly in the source evaluation.
2. **Try alternatives:**
   - Search for the same article title/headline in Google to find cached or syndicated versions
   - Check if the fact-check organization has a summary on a different page
   - Use the source's search snippet from `web_search` results (often contains enough info)
   - Look for the same fact-check on a different organization's site
3. **In the Source Evaluation table**, mark the source as:
   `Access: Blocked/Paywalled — evaluated via search snippet and secondary references`
4. **Lower confidence slightly** if a key Tier 1-2 source was inaccessible and no alternative
   was found. Note this in Step 7 (Confidence Calibration) as a factor decreasing confidence.
5. **Common blocked sites:** Snopes (paywall), some academic journals (institutional access),
   some news sites (regional paywalls). This is expected — work around it, don't abandon
   the source entirely.

### What This Skill Cannot Do
- Verify images for deepfakes with certainty (can flag indicators and recommend tools:
  Google Reverse Image Search, TinEye, InVID, FotoForensics, Deepware Scanner)
- Access paywalled academic papers (can identify them and note their conclusions from
  abstracts and secondary reporting)
- Check real-time social media engagement metrics or virality data
- Provide medical, legal, or financial advice
- Replace professional human fact-checkers for high-stakes decisions
- Guarantee 100% accuracy -- AI analysis should be treated as a starting point,
  not a final authority

---

## Claude.ai Compatibility

This skill works on both **Claude Code** (with full tool access) and **Claude.ai** (limited tools).

**When `web_search` and `web_fetch` are available** (Claude Code, Claude.ai with web access):
Use them for Steps 2-4 as described. This produces the best results with real-time source
triangulation.

**When web tools are NOT available** (Claude.ai without web access, offline):
The skill still works — adapt as follows:

1. **Steps 2-4 (Source Investigation, Deep Evaluation, Origin Tracing):**
   Use knowledge from training data. Be explicit about this limitation:
   "Based on knowledge available up to [training cutoff], without real-time web verification."
   Lower confidence by one level (High → Medium, Medium → Low) compared to web-verified analysis.

2. **Step 3 (Lateral Reading):** Cannot perform live lateral reading. Instead:
   - State what you know about the source's reputation from training data
   - Recommend specific searches the user can do themselves
   - Frame this as a teaching moment: "Here is how YOU can verify this source..."

3. **Step 5 (Red Flags):** Works fully — this is text analysis, no web needed.

4. **Step 10 (Educational):** Works fully — all tips are in `educational-tips.md`.

5. **Output:** Generate the HTML card as normal. Add a notice in the header:
   "Analysis based on AI knowledge — not verified with live web sources.
   For real-time verification, use this skill in Claude Code or check the recommended sources."

6. **Mode 3 (Prebunking):** Without web search, focus on well-documented narratives
   from training data. Be explicit that the list may not reflect the very latest campaigns.
   Recommend the user check EUvsDisinfo.eu and Factcheck.bg for current updates.

**Key principle:** A knowledge-based analysis with clear limitations stated is more valuable
than no analysis at all. The educational component (Step 10) works identically in both
environments and is the highest long-term value output of this skill.

---

## Workflow Summary

```
INPUT (text / URL / image / two sources / topic query)
    |
    v
[Mode Detection] --> Quick / Standard / Comparison / Prebunking
    |
    v
[Step 1]  Decompose into checkable claims
    |     Present to user, ask for focus (interactive checkpoint)
    v
[Step 2]  Multi-language source search + CRAAP evaluation + source scoring
    |
    v
[Step 3]  Online Source Deep Evaluation (Lateral Reading Protocol)
    |     Site credibility audit + Author check + Evidence evaluation
    |     Cross-reference check + Source evaluation summary
    v
[Step 4]  Origin tracing (first appearance, language, mutations, campaign links)
    |
    v
[Step 5]  Red flag detection (6 categories, 40+ markers, severity scoring)
    |
    v
[Step 6]  Verdict assignment (6-point scale, per-claim + overall)
    |     + Severity Score (MFS = CFS*0.50 + MTS*0.30 + SCD*0.20)
    v
[Step 7]  Confidence calibration (transparent factor analysis)
    |
    v
[Step 8]  Chain of reasoning (step-by-step logic for non-obvious verdicts)
    |
    v
[Step 9]  Counterfactual analysis ("What would make this true?")
    |
    v
[Step 10] Educational component (Teach the User to Fish)
    |     10a: Manipulation technique recognition (structured mini-lessons)
    |     10b: Lateral reading method (Stanford COR, 4-step protocol)
    |     10c: Source credibility lesson (5 questions for any source)
    |     10d: Known narrative alert (documented disinfo patterns)
    |     10e: Prebunking vaccine (inoculation against technique)
    |     10f: Domain-specific guidance (health / geopolitical)
    v
[Step 11] Output generation
    |
    +--> HTML Fact-Check Card (full visual report with MFS score)
    +--> Share-Safe Summary (copy-ready neutral text for social media responses)
```
