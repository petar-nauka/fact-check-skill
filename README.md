# Fact-Check Skill for Claude

Advanced semi-automated fact-checking, disinformation detection, and media literacy skill for Claude Code and Claude.ai.

Codex-only fact-check skill for verifying claims, comparing sources, and spotting misinformation. (fact-check-skill-codex-only.zip)

## What it does

Produces visual **Fact-Check Cards** (HTML) with verdict, confidence calibration, source scoring, manipulation technique detection, origin tracing, and educational tips.

Combines the **SIFT methodology**, the **CRAAP test**, **prebunking/inoculation science**, and **claim decomposition** with multi-language source triangulation.

### 4 Operating Modes

| Mode | Trigger | Output |
|------|---------|--------|
| **Standard** | "fact check this", "is this true?", paste text/URL | Full HTML Fact-Check Card |
| **Comparison** | "compare these sources", two URLs/texts | Comparison Card |
| **Prebunking** | "what false narratives about X?" | Prebunking Briefing Card |
| **Quick Check** | Simple yes/no question | Text verdict with sources |

### Key Features

- **11-step analysis pipeline** with claim decomposition, multi-language search, lateral reading, origin tracing, red flag detection (40+ markers across 6 categories), and MFS severity scoring
- **Educational component** — teaches users to independently evaluate information (manipulation technique recognition, lateral reading method, source credibility lessons, prebunking vaccines)
- **Multi-language support** — searches across languages relevant to the claim (English, local language, source language)
- **Works on Claude.ai** without web tools (knowledge-based fallback with stated limitations)
- **Consistent HTML output** with dark/light theme, print support, mobile-friendly, WCAG AA contrast

## Installation

### Claude Code

Copy the skill files to your Claude Code skills directory:

```bash
mkdir -p ~/.claude/skills/fact-check
cp SKILL.md ~/.claude/skills/fact-check/
cp educational-tips.md ~/.claude/skills/fact-check/
```

### Claude.ai

Upload `fact-check.skill` as a custom skill in Claude.ai settings.

## Files

| File | Description |
|------|-------------|
| `SKILL.md` | Main skill file — instructions, pipeline, output format |
| `educational-tips.md` | Reference database of manipulation techniques, cognitive biases, and defense tips |
| `CHANGELOG.md` | Version history |
| `fact-check.skill` | Pre-packaged skill file for Claude.ai upload |

## Usage Examples

```
"I saw this post on Facebook: 'The EU has banned home gardens! Starting 2026,
anyone growing their own vegetables without a permit will be fined up to €5000.
Share before they delete this!' Is this true?"

"Is it true that NASA confirmed 3 days of complete darkness in December 2026?"

"Compare these two articles about climate change: [URL1] [URL2]"

"What false narratives are currently spreading about vaccines in Europe?"
```

## Research Basis

- Fact-check labels reduce belief in false claims by ~18% (Clayton et al., 2020)
- Accuracy prompts reduce sharing of false news by 15-20% (Pennycook & Rand, 2021)
- Prebunking videos improve manipulation recognition by ~5% (van der Linden et al., 2022)
- Lateral reading is the most effective verification technique (Stanford COR, 2023)

## License

MIT
