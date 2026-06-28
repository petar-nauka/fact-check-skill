# Fact Check Skill Changelog

## v3.1

- Expanded `references/educational-tips.md` into a full media-literacy base: per-technique
  defenses with prebunking "vaccine" framing, a cognitive-biases reference, research citations,
  general tips (10-second rule, SIFT, lateral reading, image verification), and a **native
  Bulgarian educational base** for Bulgarian-language output.
- Added `references/bulgarian-context.md` covering Bulgarian information-space narratives,
  recurring disinformation patterns, and local data points. Complements the source/search lists
  in `bg-eu-sources.md`.
- Broadened the red-flag taxonomy in `references/red-flags.md` (more logical-fallacy and
  health-specific markers) while keeping the existing JSON `severity` scale and the `red_flags[]`
  schema unchanged.
- `SKILL.md`: added an explicit **Step 0** date-anchoring instruction, a **satire/opinion guard**
  in the non-negotiables, a **corrections-and-updates** (revisions) policy, and Bulgarian/English
  trigger phrases for better discovery.
- Harmonized the example red-flag codes in the test fixtures with the expanded taxonomy. No
  change to the JSON schema, result validator, renderer, packaging, or test behavior.

## v3.0

- Reworked the skill from one large `SKILL.md` into a concise progressive-disclosure
  structure with dedicated `references/` files.
- Added prompt-injection guardrails for untrusted user, screenshot, and fetched
  source content.
- Added an evidence-led workflow with explicit evidence ledger fields, source
  independence tracking, and access limitations.
- Added Bulgarian/EU source guidance for local fact-checking, EU policy, health,
  science, statistics, and geopolitical claims.
- Added MFS calibration notes and clarified that MFS is a heuristic risk score,
  not a probability.
- Added JSON result schema plus deterministic validation and HTML rendering
  scripts.
- Added regression fixtures and unit tests for standard, comparison, and
  prebunking modes.
- Added repository-level CI to validate skill metadata, run renderer tests, and
  build upload archives.
- Removed committed generated `.skill` and `.zip` artifacts from source control;
  build them from `scripts/package_skill.py` instead.

## v2.1

- Expanded lateral reading, source evaluation, MFS scoring, and educational
  sections in the previous monolithic skill file.

## v2.0

- Added standard, comparison, prebunking, and quick-check modes.
- Added source scoring, red-flag detection, origin tracing, confidence
  calibration, and share-safe summaries.

## v1.0

- Initial fact-checking workflow with claim decomposition, source checking, red
  flags, verdicts, and educational tips.
