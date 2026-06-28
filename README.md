# Fact Check Skill

Codex skill for evidence-led fact-checking, source credibility evaluation,
misinformation-risk scoring, prebunking briefings, and HTML Fact-Check Cards.

This version keeps `SKILL.md` short and uses progressive disclosure:

- `SKILL.md` contains trigger metadata, guardrails, mode selection, and the core
  workflow.
- `references/` contains detailed source-evaluation, red-flag, MFS,
  Bulgarian/EU source, and output guidance.
- `schema/` defines the JSON result contract.
- `scripts/` validates results, renders HTML cards, and builds clean upload
  archives.
- `tests/` contains regression fixtures for standard, comparison, and prebunking
  modes.

## Validate

From the repository root:

```powershell
python .\scripts\validate_skill.py .
python -m unittest discover -s tests
```

## Render a Sample Card

```powershell
python scripts\render_card.py tests\fixtures\standard_health.json --output out\standard_health.html
```

## Build Archives

Codex-style archive with `fact-check/` as the archive root:

```powershell
python scripts\package_skill.py --layout folder --output dist\fact-check-codex.zip
```

ChatGPT upload archive with `SKILL.md` at the archive root:

```powershell
python scripts\package_skill.py --layout root --output dist\fact-check-chatgpt-upload.zip
```

Generated archives intentionally exclude tests, `out/`, `dist/`, cache files, and
previous package artifacts.

## Local Codex Install

Install by copying the `fact-check` directory to:

```text
C:\Users\******\.codex\skills\fact-check
```

Keep a backup of any existing installed skill before replacing it.
