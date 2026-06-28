#!/usr/bin/env python3
"""Validate a fact-check result JSON file without third-party dependencies."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

MODES = {"quick", "standard", "comparison", "prebunking"}
VERDICTS = {"confirmed", "mostly_true", "mixed", "unverified", "misleading", "false"}
CONFIDENCE = {"low", "medium", "high"}


def configure_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")


def compute_mfs(scores: dict[str, Any]) -> float:
    return round(float(scores["cfs"]) * 0.50 + float(scores["mts"]) * 0.30 + float(scores["scd"]) * 0.20, 1)


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _require(mapping: dict[str, Any], key: str, context: str, errors: list[str]) -> Any:
    if key not in mapping:
        errors.append(f"{context}: missing required field '{key}'")
        return None
    return mapping[key]


def _validate_scores(data: dict[str, Any], mode: str, errors: list[str]) -> None:
    if mode in {"standard", "comparison"}:
        scores = data.get("scores")
        if not isinstance(scores, dict):
            errors.append("scores: required for standard and comparison modes")
            return
        for key in ("cfs", "mts", "scd"):
            value = _require(scores, key, "scores", errors)
            if value is None:
                continue
            if not _is_number(value) or not 0 <= float(value) <= 100:
                errors.append(f"scores.{key}: must be a number from 0 to 100")
        if all(_is_number(scores.get(key)) for key in ("cfs", "mts", "scd")):
            expected = compute_mfs(scores)
            if "mfs" in scores and abs(float(scores["mfs"]) - expected) > 1.0:
                errors.append(f"scores.mfs: expected about {expected}, got {scores['mfs']}")
            scores.setdefault("mfs", expected)
    elif "scores" in data:
        errors.append(f"scores: omit for {mode} mode")


def _validate_sources(data: dict[str, Any], errors: list[str]) -> set[str]:
    sources = data.get("sources")
    if not isinstance(sources, list) or not sources:
        errors.append("sources: must be a non-empty list")
        return set()

    source_ids: set[str] = set()
    for index, source in enumerate(sources, start=1):
        context = f"sources[{index}]"
        if not isinstance(source, dict):
            errors.append(f"{context}: must be an object")
            continue
        for key in ("id", "name", "tier", "site_rating", "evidence_quality", "contribution"):
            _require(source, key, context, errors)
        source_id = source.get("id")
        if isinstance(source_id, str):
            if source_id in source_ids:
                errors.append(f"{context}.id: duplicate source id '{source_id}'")
            source_ids.add(source_id)
        tier = source.get("tier")
        if not isinstance(tier, int) or isinstance(tier, bool) or not 1 <= tier <= 8:
            errors.append(f"{context}.tier: must be an integer from 1 to 8")
    return source_ids


def _validate_claims(data: dict[str, Any], mode: str, source_ids: set[str], errors: list[str]) -> None:
    claims = data.get("claims")
    if mode != "prebunking":
        if not isinstance(claims, list) or not claims:
            errors.append("claims: must be a non-empty list outside prebunking mode")
            return
    elif claims is None:
        return

    if not isinstance(claims, list):
        errors.append("claims: must be a list")
        return

    claim_ids: set[str] = set()
    for index, claim in enumerate(claims, start=1):
        context = f"claims[{index}]"
        if not isinstance(claim, dict):
            errors.append(f"{context}: must be an object")
            continue
        for key in ("id", "text", "type", "verdict", "reasoning", "source_ids"):
            _require(claim, key, context, errors)
        claim_id = claim.get("id")
        if isinstance(claim_id, str):
            if claim_id in claim_ids:
                errors.append(f"{context}.id: duplicate claim id '{claim_id}'")
            claim_ids.add(claim_id)
        verdict = claim.get("verdict")
        if verdict not in VERDICTS:
            errors.append(f"{context}.verdict: must be one of {sorted(VERDICTS)}")
        refs = claim.get("source_ids")
        if not isinstance(refs, list):
            errors.append(f"{context}.source_ids: must be a list")
            continue
        for ref in refs:
            if ref not in source_ids:
                errors.append(f"{context}.source_ids: unknown source id '{ref}'")


def _validate_narratives(data: dict[str, Any], mode: str, source_ids: set[str], errors: list[str]) -> None:
    narratives = data.get("narratives")
    if mode == "prebunking":
        if not isinstance(narratives, list) or not narratives:
            errors.append("narratives: must be a non-empty list for prebunking mode")
            return
    elif narratives is None:
        return

    if not isinstance(narratives, list):
        errors.append("narratives: must be a list")
        return

    for index, narrative in enumerate(narratives, start=1):
        context = f"narratives[{index}]"
        if not isinstance(narrative, dict):
            errors.append(f"{context}: must be an object")
            continue
        for key in ("id", "claim", "techniques", "spread_level", "truth", "defense_tip", "source_ids"):
            _require(narrative, key, context, errors)
        refs = narrative.get("source_ids")
        if not isinstance(refs, list):
            errors.append(f"{context}.source_ids: must be a list")
            continue
        for ref in refs:
            if ref not in source_ids:
                errors.append(f"{context}.source_ids: unknown source id '{ref}'")


def _validate_red_flags(data: dict[str, Any], errors: list[str]) -> None:
    flags = data.get("red_flags", [])
    if not isinstance(flags, list):
        errors.append("red_flags: must be a list")
        return
    for index, flag in enumerate(flags, start=1):
        context = f"red_flags[{index}]"
        if not isinstance(flag, dict):
            errors.append(f"{context}: must be an object")
            continue
        for key in ("code", "label", "severity", "explanation"):
            _require(flag, key, context, errors)


def validate(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for key in ("metadata", "content_summary", "overall_verdict", "sources", "share_safe_summary", "disclaimer"):
        _require(data, key, "result", errors)

    metadata = data.get("metadata")
    if not isinstance(metadata, dict):
        errors.append("metadata: must be an object")
        return errors
    mode = metadata.get("mode")
    if mode not in MODES:
        errors.append(f"metadata.mode: must be one of {sorted(MODES)}")
        mode = "standard"
    for key in ("language", "analysis_date"):
        _require(metadata, key, "metadata", errors)

    verdict = data.get("overall_verdict")
    if not isinstance(verdict, dict):
        errors.append("overall_verdict: must be an object")
    else:
        for key in ("verdict", "confidence_level", "summary"):
            _require(verdict, key, "overall_verdict", errors)
        if verdict.get("verdict") not in VERDICTS:
            errors.append(f"overall_verdict.verdict: must be one of {sorted(VERDICTS)}")
        if verdict.get("confidence_level") not in CONFIDENCE:
            errors.append(f"overall_verdict.confidence_level: must be one of {sorted(CONFIDENCE)}")

    source_ids = _validate_sources(data, errors)
    _validate_claims(data, str(mode), source_ids, errors)
    _validate_narratives(data, str(mode), source_ids, errors)
    _validate_red_flags(data, errors)
    _validate_scores(data, str(mode), errors)
    return errors


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
    args = parser.parse_args(argv)

    try:
        data = load_json(args.result_json)
    except Exception as exc:  # noqa: BLE001 - CLI should show parse failures plainly.
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    errors = validate(data)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    mode = data["metadata"]["mode"]
    suffix = ""
    if mode in {"standard", "comparison"}:
        suffix = f" (MFS {data['scores']['mfs']})"
    print(f"OK: result JSON is valid{suffix}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
