#!/usr/bin/env python3
"""Render a validated fact-check result JSON file as a self-contained HTML card."""

from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from validate_result import compute_mfs, validate  # noqa: E402


BADGE_CLASS = {
    "confirmed": "badge-confirmed",
    "mostly_true": "badge-mostly-true",
    "mixed": "badge-mixed",
    "unverified": "badge-unverified",
    "misleading": "badge-misleading",
    "false": "badge-false",
}

VERDICT_LABEL = {
    "confirmed": "Confirmed",
    "mostly_true": "Mostly true",
    "mixed": "Mixed",
    "unverified": "Unverified",
    "misleading": "Misleading",
    "false": "False",
}


def configure_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def slug_label(value: str) -> str:
    return value.replace("_", " ").title()


def badge(verdict: str) -> str:
    label = VERDICT_LABEL.get(verdict, slug_label(verdict))
    css_class = BADGE_CLASS.get(verdict, "badge-unverified")
    return f'<span class="badge {css_class}">{esc(label)}</span>'


def tier_badge(tier: int) -> str:
    return f'<span class="tier tier-{tier}">T{tier}</span>'


def section(title: str, body: str) -> str:
    if not body.strip():
        return ""
    return f"<section><h2>{esc(title)}</h2>{body}</section>"


def render_scores(data: dict[str, Any]) -> str:
    scores = data.get("scores")
    if not scores:
        return ""
    mfs = scores.get("mfs", compute_mfs(scores))
    interpretation = scores.get("interpretation", "")
    rows = "".join(
        f"<li><strong>{label}</strong>: {esc(scores[key])}/100</li>"
        for key, label in (("cfs", "CFS"), ("mts", "MTS"), ("scd", "SCD"))
    )
    return section(
        "MFS Score",
        f"""
        <div class="score-wrap">
          <div class="score" style="--score:{esc(mfs)}"><span>{esc(mfs)}</span></div>
          <div>
            <p class="muted">{esc(interpretation)}</p>
            <ul class="compact">{rows}</ul>
          </div>
        </div>
        """,
    )


def render_claims(data: dict[str, Any], sources_by_id: dict[str, dict[str, Any]]) -> str:
    claims = data.get("claims") or []
    if not claims:
        return ""
    parts: list[str] = []
    for claim in claims:
        source_links = []
        for source_id in claim.get("source_ids", []):
            source = sources_by_id.get(source_id)
            if source:
                source_links.append(f"{esc(source_id)}: {esc(source.get('name', source_id))}")
            else:
                source_links.append(esc(source_id))
        source_text = "; ".join(source_links) if source_links else "No linked source"
        parts.append(
            f"""
            <article class="item">
              <div class="item-head">
                <strong>{esc(claim.get('id', 'Claim'))}</strong>
                {badge(str(claim.get('verdict', 'unverified')))}
              </div>
              <p>{esc(claim.get('text', ''))}</p>
              <p class="muted">Type: {esc(claim.get('type', 'factual'))}</p>
              <details>
                <summary>Reasoning and sources</summary>
                <p>{esc(claim.get('reasoning', ''))}</p>
                <p class="muted">{source_text}</p>
              </details>
            </article>
            """
        )
    return section("Claims Breakdown", "".join(parts))


def render_narratives(data: dict[str, Any], sources_by_id: dict[str, dict[str, Any]]) -> str:
    narratives = data.get("narratives") or []
    if not narratives:
        return ""
    parts: list[str] = []
    for narrative in narratives:
        source_text = ", ".join(
            esc(sources_by_id.get(source_id, {}).get("name", source_id))
            for source_id in narrative.get("source_ids", [])
        )
        techniques = ", ".join(esc(item) for item in narrative.get("techniques", []))
        parts.append(
            f"""
            <article class="item">
              <div class="item-head">
                <strong>{esc(narrative.get('id', 'Narrative'))}</strong>
                <span class="pill">{esc(narrative.get('spread_level', 'unknown'))}</span>
              </div>
              <p><strong>Claim:</strong> {esc(narrative.get('claim', ''))}</p>
              <p><strong>Truth:</strong> {esc(narrative.get('truth', ''))}</p>
              <p class="muted">Techniques: {techniques}</p>
              <p><strong>Defense tip:</strong> {esc(narrative.get('defense_tip', ''))}</p>
              <p class="muted">Sources: {source_text}</p>
            </article>
            """
        )
    return section("Active Narratives", "".join(parts))


def render_flags(data: dict[str, Any]) -> str:
    flags = data.get("red_flags") or []
    if not flags:
        return ""
    items = "".join(
        f"""
        <li>
          <strong>{esc(flag.get('code', ''))} - {esc(flag.get('label', ''))}</strong>
          <span class="muted">({esc(flag.get('severity', ''))})</span><br>
          {esc(flag.get('explanation', ''))}
        </li>
        """
        for flag in flags
    )
    return section("Red Flags Detected", f'<ul class="spaced">{items}</ul>')


def render_sources(data: dict[str, Any]) -> str:
    sources = data.get("sources") or []
    rows = []
    for source in sources:
        url = source.get("url")
        name = esc(source.get("name", "Source"))
        title = f'<a href="{esc(url)}">{name}</a>' if url else name
        rows.append(
            f"""
            <article class="source item">
              <div class="item-head">
                <strong>{esc(source.get('id', 'S'))}. {title}</strong>
                {tier_badge(int(source.get('tier', 8)))}
              </div>
              <p>{esc(source.get('contribution', ''))}</p>
              <dl>
                <dt>Site</dt><dd>{esc(source.get('site_rating', 'not assessed'))}</dd>
                <dt>Evidence</dt><dd>{esc(source.get('evidence_quality', 'not assessed'))}</dd>
                <dt>Author</dt><dd>{esc(source.get('author', 'not specified'))}</dd>
                <dt>Access</dt><dd>{esc(source.get('access_note', 'full or not specified'))}</dd>
              </dl>
            </article>
            """
        )
    return section("Evidence Ledger", "".join(rows))


def render_education(data: dict[str, Any]) -> str:
    notes = data.get("educational_notes") or []
    if not notes:
        return ""
    items = "".join(f"<li>{esc(note)}</li>" for note in notes)
    return section("Educational Notes", f'<ul class="spaced">{items}</ul>')


def render_html(data: dict[str, Any]) -> str:
    errors = validate(data)
    if errors:
        joined = "\n".join(errors)
        raise ValueError(f"invalid result JSON:\n{joined}")

    metadata = data["metadata"]
    verdict = data["overall_verdict"]
    sources_by_id = {source["id"]: source for source in data.get("sources", [])}
    mode = str(metadata["mode"])
    body = "\n".join(
        [
            section("Original Content Summary", f"<p>{esc(data['content_summary'])}</p>"),
            section(
                "Overall Verdict",
                f"""
                <div class="verdict-line">
                  {badge(str(verdict['verdict']))}
                  <span class="confidence">Confidence: {esc(verdict['confidence_level'])}</span>
                </div>
                <p>{esc(verdict['summary'])}</p>
                """,
            ),
            render_scores(data),
            render_claims(data, sources_by_id),
            render_narratives(data, sources_by_id),
            render_flags(data),
            render_sources(data),
            render_education(data),
            section("Share-Safe Summary", f"<blockquote>{esc(data['share_safe_summary'])}</blockquote>"),
            section("Disclaimer", f"<p class=\"muted\">{esc(data['disclaimer'])}</p>"),
        ]
    )

    title = "Fact-Check Card"
    if mode == "prebunking":
        title = "Prebunking Briefing"
    return f"""<!doctype html>
<html lang="{esc(metadata.get('language', 'en'))}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <style>
    :root {{
      --bg: #ffffff;
      --bg-secondary: #f8f9fa;
      --bg-tertiary: #f1f3f5;
      --text: #1a1a1a;
      --text-secondary: #495057;
      --text-tertiary: #868e96;
      --border: #dee2e6;
      --border-light: #e9ecef;
      --green: #16a34a;
      --lime: #65a30d;
      --yellow: #ca8a04;
      --orange: #ea580c;
      --red-orange: #dc2626;
      --dark-red: #991b1b;
      --shadow: 0 1px 3px rgba(0,0,0,0.08);
      --shadow-md: 0 4px 12px rgba(0,0,0,0.1);
      --radius: 8px;
      --radius-sm: 4px;
    }}
    @media (prefers-color-scheme: dark) {{
      :root {{
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
      }}
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg-secondary);
      color: var(--text);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
      line-height: 1.5;
    }}
    .container {{
      max-width: 800px;
      margin: 0 auto;
      padding: 24px 16px 48px;
    }}
    header, section {{
      background: var(--bg);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
      margin-bottom: 16px;
      padding: 20px;
    }}
    h1, h2 {{ margin: 0 0 12px; line-height: 1.2; }}
    h1 {{ font-size: 28px; }}
    h2 {{ font-size: 20px; }}
    p {{ margin: 0 0 12px; }}
    a {{ color: inherit; }}
    .meta, .muted {{ color: var(--text-secondary); }}
    .badge, .tier, .pill {{
      display: inline-flex;
      align-items: center;
      min-height: 24px;
      border-radius: 999px;
      font-size: 12px;
      font-weight: 700;
      padding: 3px 8px;
      white-space: nowrap;
    }}
    .badge-confirmed {{ background: var(--green); color: #fff; }}
    .badge-mostly-true {{ background: var(--lime); color: #fff; }}
    .badge-mixed {{ background: var(--yellow); color: #fff; }}
    .badge-unverified {{ background: var(--orange); color: #fff; }}
    .badge-misleading {{ background: var(--red-orange); color: #fff; }}
    .badge-false {{ background: var(--dark-red); color: #fff; }}
    .tier-1, .tier-2 {{ background: #dcfce7; color: #166534; }}
    .tier-3, .tier-4 {{ background: #dbeafe; color: #1e40af; }}
    .tier-5, .tier-6 {{ background: #fef9c3; color: #854d0e; }}
    .tier-7, .tier-8 {{ background: #fecaca; color: #991b1b; }}
    .pill {{ background: var(--bg-tertiary); color: var(--text-secondary); }}
    .verdict-line, .item-head, .score-wrap {{
      display: flex;
      align-items: center;
      gap: 12px;
      justify-content: space-between;
      flex-wrap: wrap;
    }}
    .item {{
      border: 1px solid var(--border-light);
      border-radius: var(--radius);
      padding: 14px;
      margin-top: 12px;
      background: var(--bg-secondary);
    }}
    details {{
      border-top: 1px solid var(--border-light);
      margin-top: 10px;
      padding-top: 10px;
    }}
    summary {{ cursor: pointer; font-weight: 700; }}
    .score {{
      --score: 0;
      width: 120px;
      height: 120px;
      border-radius: 50%;
      display: grid;
      place-items: center;
      background: conic-gradient(var(--orange) calc(var(--score) * 1%), var(--bg-tertiary) 0);
      flex: 0 0 auto;
    }}
    .score span {{
      width: 82px;
      height: 82px;
      border-radius: 50%;
      display: grid;
      place-items: center;
      background: var(--bg);
      font-size: 28px;
      font-weight: 700;
    }}
    .compact, .spaced {{ margin: 0; padding-left: 20px; }}
    .spaced li {{ margin-bottom: 10px; }}
    dl {{
      display: grid;
      grid-template-columns: 110px 1fr;
      gap: 6px 12px;
      margin: 0;
    }}
    dt {{ color: var(--text-secondary); font-weight: 700; }}
    dd {{ margin: 0; }}
    blockquote {{
      margin: 0;
      padding: 12px 14px;
      border-left: 4px solid var(--border);
      background: var(--bg-secondary);
    }}
    @media (max-width: 520px) {{
      .container {{ padding: 12px 10px 32px; }}
      header, section {{ padding: 14px; }}
      h1 {{ font-size: 24px; }}
      dl {{ grid-template-columns: 1fr; }}
      .score-wrap {{ align-items: flex-start; }}
    }}
    @media print {{
      body {{ background: #fff; }}
      header, section {{ box-shadow: none; break-inside: avoid; }}
      details {{ display: block; }}
    }}
  </style>
</head>
<body>
  <main class="container">
    <header>
      <h1>{esc(title)}</h1>
      <p class="meta">Mode: {esc(slug_label(mode))} | Date: {esc(metadata['analysis_date'])} | Language: {esc(metadata['language'])}</p>
      {f'<p class="meta">Topic: {esc(metadata["topic"])}</p>' if metadata.get("topic") else ''}
    </header>
    {body}
  </main>
</body>
</html>
"""


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("top-level JSON value must be an object")
    return data


def main(argv: list[str] | None = None) -> int:
    configure_stdio()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("result_json", type=Path)
    parser.add_argument("--output", "-o", type=Path)
    args = parser.parse_args(argv)

    try:
        html_text = render_html(load_json(args.result_json))
    except Exception as exc:  # noqa: BLE001 - CLI should surface validation/render errors.
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(html_text, encoding="utf-8")
        print(f"Wrote {args.output}")
    else:
        print(html_text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
