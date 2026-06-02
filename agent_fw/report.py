"""report.py — HTML 儀表板產生器。

給 GUI 介面使用：把框架當前狀態變成可瀏覽的 HTML。
- 零外部依賴（純 HTML + CSS + 一點 vanilla JS）
- 響應式、可列印
- 直接在瀏覽器開，無需 server
"""

from __future__ import annotations

import html
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from . import core, ui, version, detection, validate


def generate(root: Path, output: Optional[Path] = None) -> Path:
    root = Path(root)
    if output is None:
        output = root / "framework-dashboard.html"
    output = Path(output)

    manifest = version.get_current(root)
    det = detection.run_all(root)
    val = validate.run_all(root)

    # 收集 cognitive-frameworks 清單
    cf_dir = root / "cognitive-frameworks"
    cfs: list = []
    if cf_dir.is_dir():
        for fw in sorted(cf_dir.iterdir()):
            if not fw.is_dir() or fw.name == "_template":
                continue
            meta = fw / "META.md"
            if meta.is_file():
                fm = core.extract_metadata(meta)
                cfs.append({
                    "slug": fw.name,
                    "name": fm.get("framework-name", fw.name),
                    "version": fm.get("framework-version", "?"),
                    "status": fm.get("status", "?"),
                    "tags": fm.get("tags", ""),
                })

    # 收集 CHANGELOG 條目
    cl_path = root / "CHANGELOG.md"
    changelog: list = []
    if cl_path.is_file():
        for e in core.ChangelogEntry.parse_file(core.read_text(cl_path))[:10]:
            changelog.append({
                "version": e.version,
                "date": e.date,
                "body": e.body[:500],
            })

    html_text = _render_html(
        version=str(manifest.version),
        last_updated=manifest.last_updated,
        status=manifest.framework_status,
        detection=det,
        validation=val,
        frameworks=cfs,
        changelog=changelog,
    )
    core.write_text(output, html_text)
    return output


def _render_html(version: str, last_updated: str, status: str,
                 detection: detection.DetectionReport,
                 validation: validate.ValidationReport,
                 frameworks: list,
                 changelog: list) -> str:
    det_overall_badge = {
        "clean": ("✓ CLEAN", "#22c55e"),
        "minor": ("⚠ MINOR", "#eab308"),
        "major": ("✗ MAJOR", "#ef4444"),
    }[detection.overall]

    val_status = "✓ 全部通過" if validation.failed == 0 else f"✗ {validation.failed} 項失敗"

    findings_html = ""
    for f in detection.findings:
        sev_color = {"high": "#ef4444", "medium": "#eab308", "low": "#6b7280"}[f.severity]
        findings_html += f"""
        <div class="finding">
          <div class="finding-head">
            <span class="rule-tag">[{html.escape(f.rule)}]</span>
            <span class="sev" style="background:{sev_color}">{html.escape(f.severity.upper())}</span>
          </div>
          <div class="evidence">{html.escape(f.evidence)}</div>
          <div class="reco">→ {html.escape(f.recommendation)}</div>
        </div>"""

    if not detection.findings:
        findings_html = '<p class="empty">無觸發 — framework 內容一致。</p>'

    frameworks_rows = "".join(
        f'<tr><td><code>{html.escape(f["slug"])}</code></td>'
        f'<td>{html.escape(f["name"])}</td>'
        f'<td><code>{html.escape(f["version"])}</code></td>'
        f'<td><span class="pill">{html.escape(f["status"])}</span></td></tr>'
        for f in frameworks
    )

    changelog_html = "".join(
        f'<details><summary><strong>[{html.escape(e["version"])}]</strong> {html.escape(e["date"])}</summary>'
        f'<pre>{html.escape(e["body"])}</pre></details>'
        for e in changelog
    )

    issues_html = "".join(
        f'<li class="err">✗ <strong>{html.escape(n)}</strong>: {html.escape(d)}</li>'
        for n, d in validation.issues
    )
    warnings_html = "".join(
        f'<li class="warn">⚠ <strong>{html.escape(n)}</strong>: {html.escape(d)}</li>'
        for n, d in validation.warnings_list
    )

    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Agent Framework Dashboard — v{html.escape(version)}</title>
<style>
  * {{ box-sizing: border-box; }}
  body {{
    font-family: -apple-system, "Segoe UI", "Noto Sans TC", "PingFang TC", "Microsoft JhengHei", sans-serif;
    margin: 0; padding: 24px;
    background: #0f172a; color: #e2e8f0;
    line-height: 1.6;
  }}
  h1, h2, h3 {{ margin: 0 0 12px 0; }}
  h1 {{ font-size: 28px; color: #38bdf8; }}
  h2 {{ font-size: 20px; color: #a5b4fc; border-bottom: 1px solid #334155; padding-bottom: 6px; margin-top: 32px; }}
  h3 {{ font-size: 16px; color: #cbd5e1; }}
  code {{ background: #1e293b; padding: 2px 6px; border-radius: 4px; color: #fcd34d; font-size: 13px; }}
  .card {{ background: #1e293b; border-radius: 8px; padding: 16px 20px; margin: 12px 0; border: 1px solid #334155; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; }}
  .stat {{ background: #1e293b; padding: 16px; border-radius: 8px; border: 1px solid #334155; }}
  .stat .label {{ color: #94a3b8; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; }}
  .stat .value {{ font-size: 24px; font-weight: bold; color: #f1f5f9; margin-top: 4px; }}
  .badge {{ display: inline-block; padding: 4px 10px; border-radius: 4px; font-weight: bold; font-size: 13px; }}
  .finding {{ background: #1e293b; border-left: 4px solid #64748b; padding: 10px 14px; margin: 8px 0; border-radius: 4px; }}
  .finding-head {{ display: flex; gap: 8px; align-items: center; margin-bottom: 6px; }}
  .rule-tag {{ color: #38bdf8; font-weight: bold; }}
  .sev {{ padding: 2px 8px; border-radius: 3px; font-size: 11px; color: #fff; font-weight: bold; }}
  .evidence {{ color: #cbd5e1; font-size: 14px; }}
  .reco {{ color: #94a3b8; font-size: 13px; margin-top: 4px; font-style: italic; }}
  table {{ width: 100%; border-collapse: collapse; }}
  th, td {{ text-align: left; padding: 8px 12px; border-bottom: 1px solid #334155; }}
  th {{ color: #94a3b8; font-size: 12px; text-transform: uppercase; }}
  .pill {{ background: #334155; padding: 2px 8px; border-radius: 12px; font-size: 12px; }}
  details {{ background: #1e293b; padding: 8px 12px; margin: 4px 0; border-radius: 4px; }}
  summary {{ cursor: pointer; padding: 4px 0; }}
  pre {{ white-space: pre-wrap; word-wrap: break-word; font-size: 12px; color: #cbd5e1; }}
  .empty {{ color: #64748b; font-style: italic; }}
  .err {{ color: #fca5a5; }}
  .warn {{ color: #fcd34d; }}
  .footer {{ text-align: center; color: #64748b; font-size: 12px; margin-top: 48px; padding-top: 16px; border-top: 1px solid #334155; }}
  @media print {{
    body {{ background: #fff; color: #000; }}
    .card, .stat, .finding, details {{ background: #f8fafc; border-color: #cbd5e1; }}
    h1, h2, h3 {{ color: #0f172a; }}
  }}
</style>
</head>
<body>

<h1>🤖 Agent Framework Dashboard</h1>
<p>v{html.escape(version)} · 最後更新：{html.escape(last_updated) or "?"} · 狀態：<span class="pill">{html.escape(status)}</span></p>

<div class="grid">
  <div class="stat">
    <div class="label">Framework Version</div>
    <div class="value">{html.escape(version)}</div>
  </div>
  <div class="stat">
    <div class="label">Detection Overall</div>
    <div class="value"><span class="badge" style="background:{det_overall_badge[1]}">{det_overall_badge[0]}</span></div>
  </div>
  <div class="stat">
    <div class="label">Validation</div>
    <div class="value" style="font-size:18px">{val_status}</div>
    <div style="color:#94a3b8; font-size:12px; margin-top:4px">✓ {validation.passed} 通過 · ⚠ {validation.warnings} 警告 · ✗ {validation.failed} 失敗</div>
  </div>
  <div class="stat">
    <div class="label">Cognitive Frameworks</div>
    <div class="value">{len(frameworks)}</div>
  </div>
</div>

<h2>🔍 Detection Report</h2>
<div class="card">
{findings_html}
</div>

<h2>✓ Validation Report</h2>
<div class="card">
  <ul>
    {issues_html}
    {warnings_html}
  </ul>
  {('<p class="empty">無 issue / warning。</p>' if not issues_html and not warnings_html else '')}
</div>

<h2>🧠 Cognitive Frameworks</h2>
<div class="card">
  <table>
    <thead><tr><th>Slug</th><th>名稱</th><th>版本</th><th>狀態</th></tr></thead>
    <tbody>
      {frameworks_rows or '<tr><td colspan="4" class="empty">無</td></tr>'}
    </tbody>
  </table>
</div>

<h2>📝 CHANGELOG（最近 10 條）</h2>
<div class="card">
{changelog_html or '<p class="empty">無</p>'}
</div>

<div class="footer">
  產生於 {ts} · agent-fw report
</div>

</body>
</html>
"""
