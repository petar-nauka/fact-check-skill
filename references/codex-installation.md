# Codex Installation and Validation

## Local Install

Install the skill by placing the `fact-check` directory under:

```text
$CODEX_HOME/skills/fact-check
```

If `CODEX_HOME` is unset, use the default Codex skills folder:

```text
~/.codex/skills/fact-check
```

The skill directory must contain `SKILL.md` at its root. The folder name and the
frontmatter name should both be `fact-check`.

## Validation

Run the skill metadata validator from the skill-creator system skill:

```text
python C:\Users\petar\.codex\skills\.system\skill-creator\scripts\quick_validate.py path\to\fact-check
```

Run the renderer tests:

```text
python -m unittest discover -s tests
```

Render a sample card:

```text
python scripts\render_card.py tests\fixtures\standard_health.json --output out\standard_health.html
```

## Codex Metadata

`agents/openai.yaml` provides UI metadata. Keep it short and aligned with
`SKILL.md`. Do not add tool dependencies unless the skill requires a specific MCP
or connector.
