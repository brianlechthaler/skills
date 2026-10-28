#!/usr/bin/env python3
"""Scan every skill directory with NVIDIA SkillSpector (static / --no-llm).

Discovers immediate child directories that contain SKILL.md (the layout used by
this repository), scans each one individually with --use-shipped-baseline
(honors a reviewed .skillspector-baseline.yaml in the skill directory), and
writes:

  - per-skill JSON and SARIF under --output-dir
  - a merged skillspector.sarif
  - a Markdown summary (stdout + optional --summary-file)

Exit codes follow SkillSpector's CI contract when --gate is set:
  0 = all skills scored risk <= 50 and every scan completed
  1 = at least one skill scored risk > 50, or a scan failed to execute
  2 = usage / environment error (SkillSpector missing, bad args, etc.)

Without --gate, exit 1 only when a scan fails to execute (exit 2 from the
CLI), so CI can still publish reports for an existing corpus with findings.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SARIF_SCHEMA = "https://json.schemastore.org/sarif-2.1.0.json"
SEVERITY_TO_LEVEL = {
    "CRITICAL": "error",
    "HIGH": "error",
    "MEDIUM": "warning",
    "LOW": "note",
    "INFO": "note",
}


@dataclass
class SkillResult:
    name: str
    path: Path
    returncode: int
    risk_score: int | None
    risk_severity: str | None
    recommendation: str | None
    finding_count: int | None
    error: str | None = None

    @property
    def execution_ok(self) -> bool:
        # SkillSpector: 0 = SAFE/CAUTION, 1 = DO_NOT_INSTALL / gate, 2 = error.
        return self.returncode in (0, 1) and self.error is None

    @property
    def exceeds_risk_gate(self) -> bool:
        if self.risk_score is None:
            return self.returncode == 1
        return self.risk_score > 50 or self.returncode == 1


def discover_skills(root: Path) -> list[Path]:
    return [
        path.parent
        for path in sorted(root.glob("*/SKILL.md"))
        if path.is_file() and path.parent.is_dir()
    ]


def find_skillspector() -> str:
    explicit = os.environ.get("SKILLSPECTOR_BIN")
    if explicit:
        return explicit
    found = shutil.which("skillspector")
    if found:
        return found
    user_bin = Path.home() / ".local" / "bin" / "skillspector"
    if user_bin.is_file():
        return str(user_bin)
    raise FileNotFoundError(
        "skillspector not found on PATH (install with: "
        "pip install 'git+https://github.com/NVIDIA/SkillSpector.git@v2.13.1')"
    )


def _load_json(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def json_report_to_sarif(report: dict[str, Any], skill_dir: Path) -> dict[str, Any]:
    """Build a SARIF 2.1.0 document from a SkillSpector JSON report."""
    skill_meta = report.get("skill") or {}
    skill_name = skill_meta.get("name") or skill_dir.name
    issues = report.get("issues") or []
    rules: dict[str, dict[str, Any]] = {}
    results: list[dict[str, Any]] = []

    for issue in issues:
        if not isinstance(issue, dict):
            continue
        rule_id = str(issue.get("id") or issue.get("finding_id") or "unknown")
        severity = str(issue.get("severity") or "MEDIUM").upper()
        if rule_id not in rules:
            rules[rule_id] = {
                "id": rule_id,
                "name": str(issue.get("pattern") or rule_id),
                "shortDescription": {
                    "text": str(issue.get("pattern") or rule_id),
                },
                "fullDescription": {
                    "text": str(
                        issue.get("explanation") or issue.get("finding") or rule_id
                    ),
                },
                "defaultConfiguration": {
                    "level": SEVERITY_TO_LEVEL.get(severity, "warning"),
                },
                "properties": {
                    "category": issue.get("category"),
                    "security-severity": severity.lower(),
                },
            }

        location = issue.get("location") or {}
        rel_file = str(location.get("file") or "SKILL.md")
        uri = f"{skill_dir.name}/{rel_file}".replace("\\", "/")
        start_line = location.get("start_line") or 1
        end_line = location.get("end_line") or start_line
        message = str(
            issue.get("finding")
            or issue.get("explanation")
            or issue.get("pattern")
            or rule_id
        )
        results.append(
            {
                "ruleId": rule_id,
                "level": SEVERITY_TO_LEVEL.get(severity, "warning"),
                "message": {"text": message},
                "locations": [
                    {
                        "physicalLocation": {
                            "artifactLocation": {"uri": uri},
                            "region": {
                                "startLine": int(start_line),
                                "endLine": int(end_line),
                            },
                        }
                    }
                ],
                "properties": {
                    "security-severity": severity.lower(),
                    "confidence": issue.get("confidence"),
                    "skill": skill_name,
                },
            }
        )

    risk = report.get("risk_assessment") or {}
    return {
        "version": "2.1.0",
        "$schema": SARIF_SCHEMA,
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "NVIDIA SkillSpector",
                        "informationUri": "https://github.com/NVIDIA/SkillSpector",
                        "version": str(
                            ((report.get("metadata") or {}).get("skillspector_version"))
                            or "unknown"
                        ),
                        "rules": list(rules.values()),
                    }
                },
                "results": results,
                "properties": {
                    "skill": skill_name,
                    "risk_score": risk.get("score"),
                    "risk_severity": risk.get("severity"),
                    "recommendation": risk.get("recommendation"),
                },
            }
        ],
    }


def scan_skill(
    skillspector: str,
    skill_dir: Path,
    output_dir: Path,
) -> SkillResult:
    name = skill_dir.name
    json_path = output_dir / f"{name}.json"
    sarif_path = output_dir / f"{name}.sarif"
    cmd = [
        skillspector,
        "scan",
        str(skill_dir),
        "--no-llm",
        "--use-shipped-baseline",
        "--format",
        "json",
        "--output",
        str(json_path),
    ]
    try:
        completed = subprocess.run(
            cmd,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError as exc:
        return SkillResult(
            name=name,
            path=skill_dir,
            returncode=2,
            risk_score=None,
            risk_severity=None,
            recommendation=None,
            finding_count=None,
            error=str(exc),
        )

    report = _load_json(json_path)
    risk = (report or {}).get("risk_assessment") or {}
    execution_ok = completed.returncode in (0, 1) and report is not None
    result = SkillResult(
        name=name,
        path=skill_dir,
        returncode=completed.returncode,
        risk_score=risk.get("score"),
        risk_severity=risk.get("severity"),
        recommendation=risk.get("recommendation"),
        finding_count=len((report or {}).get("issues") or []) if report else None,
        error=None
        if execution_ok
        else (completed.stderr or completed.stdout or "scan failed"),
    )

    if execution_ok and report is not None:
        sarif_path.write_text(
            json.dumps(json_report_to_sarif(report, skill_dir), indent=2) + "\n",
            encoding="utf-8",
        )
    return result


def merge_sarif(output_dir: Path, merged_path: Path) -> int:
    runs: list[dict[str, Any]] = []
    for path in sorted(output_dir.glob("*.sarif")):
        if path.resolve() == merged_path.resolve():
            continue
        doc = _load_json(path)
        if not doc:
            continue
        for run in doc.get("runs") or []:
            if isinstance(run, dict):
                runs.append(run)
    merged = {
        "version": "2.1.0",
        "$schema": SARIF_SCHEMA,
        "runs": runs,
    }
    merged_path.write_text(json.dumps(merged, indent=2) + "\n", encoding="utf-8")
    return len(runs)


def write_summary(results: list[SkillResult], summary_file: Path | None) -> str:
    lines = [
        "## SkillSpector scan",
        "",
        f"Scanned **{len(results)}** skill(s) with NVIDIA SkillSpector (`--no-llm`).",
        "",
        "| Skill | Score | Severity | Recommendation | Findings | Status |",
        "| --- | ---: | --- | --- | ---: | --- |",
    ]
    for result in results:
        if not result.execution_ok:
            status = "error"
        elif result.exceeds_risk_gate:
            status = "fail"
        else:
            status = "ok"
        lines.append(
            "| {name} | {score} | {severity} | {rec} | {findings} | {status} |".format(
                name=result.name,
                score="—" if result.risk_score is None else result.risk_score,
                severity=result.risk_severity or "—",
                rec=result.recommendation or "—",
                findings="—" if result.finding_count is None else result.finding_count,
                status=status,
            )
        )

    failed = [r for r in results if not r.execution_ok]
    gated = [r for r in results if r.execution_ok and r.exceeds_risk_gate]
    lines.extend(["", "### Totals", ""])
    lines.append(f"- Errors: **{len(failed)}**")
    lines.append(f"- Risk score > 50 (DO_NOT_INSTALL): **{len(gated)}**")
    if gated:
        lines.append(
            "- High-risk skills: "
            + ", ".join(f"`{r.name}` ({r.risk_score})" for r in gated)
        )
    if failed:
        lines.append("- Failed scans: " + ", ".join(f"`{r.name}`" for r in failed))
        for result in failed:
            if result.error:
                lines.append(
                    f"  - `{result.name}`: `{result.error.splitlines()[0][:200]}`"
                )

    text = "\n".join(lines) + "\n"
    if summary_file is not None:
        summary_file.parent.mkdir(parents=True, exist_ok=True)
        with summary_file.open("a", encoding="utf-8") as handle:
            handle.write(text)
    return text


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Repository root containing skill directories (default: cwd)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("skillspector-results"),
        help="Directory for per-skill JSON/SARIF and the merged SARIF",
    )
    parser.add_argument(
        "--summary-file",
        type=Path,
        default=None,
        help="Append a Markdown summary (e.g. $GITHUB_STEP_SUMMARY)",
    )
    parser.add_argument(
        "--gate",
        action="store_true",
        help="Exit 1 when any skill has risk score > 50 (SkillSpector default gate)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = args.root.resolve()
    output_dir = args.output_dir
    if not output_dir.is_absolute():
        output_dir = (Path.cwd() / output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        skillspector = find_skillspector()
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    skills = discover_skills(root)
    if not skills:
        print(
            f"error: no skill directories with SKILL.md under {root}",
            file=sys.stderr,
        )
        return 2

    print(f"Using {skillspector}")
    print(f"Scanning {len(skills)} skill(s) under {root}")

    results: list[SkillResult] = []
    for skill_dir in skills:
        print(f"→ {skill_dir.name}", flush=True)
        result = scan_skill(skillspector, skill_dir, output_dir)
        results.append(result)
        score = "—" if result.risk_score is None else str(result.risk_score)
        print(
            f"  exit={result.returncode} score={score} "
            f"severity={result.risk_severity or '—'} "
            f"recommendation={result.recommendation or '—'}",
            flush=True,
        )

    merged = output_dir / "skillspector.sarif"
    run_count = merge_sarif(output_dir, merged)
    print(f"Merged SARIF runs: {run_count} → {merged}")

    summary = write_summary(results, args.summary_file)
    print(summary)

    exec_failures = [r for r in results if not r.execution_ok]
    risk_failures = [r for r in results if r.execution_ok and r.exceeds_risk_gate]
    if exec_failures:
        return 1
    if args.gate and risk_failures:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
