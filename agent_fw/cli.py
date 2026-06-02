"""cli.py — 命令列入口。

所有子命令在這裡定義與分派。
"""

from __future__ import annotations

import argparse
import os
import platform
import shutil
import subprocess
import sys
import webbrowser
from datetime import datetime
from pathlib import Path
from typing import Optional

from . import __version__ as fw_version
from . import bootstrap, bump, core, detection, framework_new, handoff, prompt, report, ui, validate, version


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


# ---------------------------------------------------------------------------
# 主入口
# ---------------------------------------------------------------------------

def main(argv: Optional[list] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args) or 0
    except KeyboardInterrupt:
        ui.warn("使用者中斷")
        return 130
    except Exception as e:
        ui.error(f"{type(e).__name__}: {e}")
        if os.environ.get("AGENT_FW_DEBUG"):
            raise
        return 1


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="agent-fw",
        description="Agent Framework CLI — 自動版本感知、進度交接、多版本混雜偵測。",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--version", action="version", version=f"agent-fw {fw_version}")
    p.add_argument("--root", help="framework 根目錄（預設：自動搜尋）")
    p.add_argument("--no-color", action="store_true", help="關閉色彩輸出")

    sub = p.add_subparsers(dest="cmd", required=True, metavar="<cmd>")

    # init
    s = sub.add_parser("init", help="在當前目錄初始化 framework")
    s.set_defaults(func=_cmd_init)

    # status
    s = sub.add_parser("status", help="顯示 framework 當前狀態")
    s.set_defaults(func=_cmd_status)

    # read
    s = sub.add_parser("read", help="依協議順序讀取檔案")
    s.add_argument("path", nargs="?", help="指定檔案（省略：照 PROTOCOL 順序）")
    s.set_defaults(func=_cmd_read)

    # bootstrap
    s = sub.add_parser("bootstrap", help="跑 session 啟動流程")
    s.add_argument("--last-known", help="已知的 framework-version（用於 delta 計算）")
    s.add_argument("--handoff", help="要套用的 handoff 檔路徑")
    s.add_argument("--format", choices=["text", "yaml", "json"], default="text", help="輸出格式")
    s.set_defaults(func=_cmd_bootstrap)

    # bump
    s = sub.add_parser("bump", help="bump framework 版本")
    s.add_argument("type", choices=["major", "minor", "patch"], help="bump 類型")
    s.add_argument("--reason", required=True, help="bump 原因")
    s.add_argument("--breaking", help="破壞性變更清單（逗號分隔）")
    s.add_argument("--notes", help="額外備註")
    s.set_defaults(func=_cmd_bump)

    # detect
    s = sub.add_parser("detect", help="跑多版本混雜偵測")
    s.add_argument("--format", choices=["text", "json"], default="text")
    s.set_defaults(func=_cmd_detect)

    # validate
    s = sub.add_parser("validate", help="驗證 framework 完整性")
    s.set_defaults(func=_cmd_validate)

    # handoff
    s = sub.add_parser("handoff", help="進度交接管理")
    ho_sub = s.add_subparsers(dest="ho_cmd", required=True, metavar="<ho_cmd>")

    ho_new = ho_sub.add_parser("new", help="建立新 handoff")
    ho_new.add_argument("--task", required=True, help="任務名稱")
    ho_new.add_argument("--out", default="./handoff.md", help="輸出檔路徑")
    ho_new.add_argument("--from", dest="from_session", default="", help="來源 session 描述")
    ho_new.add_argument("--summary", default="", help="context-summary")
    ho_new.add_argument("--state", default="", help="current-state")
    ho_new.add_argument("--decisions", default="", help="decisions")
    ho_new.add_argument("--questions", default="", help="open-questions")
    ho_new.add_argument("--next", default="", help="next-actions")
    ho_new.add_argument("--frameworks", default="layered-task-execution (1.0.0)", help="loaded-frameworks")
    ho_new.set_defaults(func=_cmd_handoff_new)

    ho_val = ho_sub.add_parser("validate", help="驗證 handoff 檔")
    ho_val.add_argument("file", help="handoff 檔路徑")
    ho_val.set_defaults(func=_cmd_handoff_validate)

    # new-framework
    s = sub.add_parser("new-framework", help="建立新認知框架")
    s.add_argument("slug", help="framework slug（kebab-case）")
    s.add_argument("--name", help="framework 名稱")
    s.add_argument("--one-liner", help="一句話定義")
    s.set_defaults(func=_cmd_new_framework)

    # prompt
    s = sub.add_parser("prompt", help="產生給 AI 的 system prompt")
    s.add_argument("--for", dest="target", default="generic", choices=["generic", "claude", "code-assistant"], help="目標 AI 類型")
    s.add_argument("-o", "--output", help="輸出檔（預設 stdout）")
    s.add_argument("--extra", help="補充脈絡")
    s.set_defaults(func=_cmd_prompt)

    # report
    s = sub.add_parser("report", help="產生 HTML 儀表板")
    s.add_argument("-o", "--output", help="輸出檔（預設 framework-dashboard.html）")
    s.add_argument("--open", action="store_true", help="產生後用瀏覽器開啟")
    s.set_defaults(func=_cmd_report)

    # tui
    s = sub.add_parser("tui", help="互動式選單")
    s.set_defaults(func=_cmd_tui)

    # install / uninstall
    s = sub.add_parser("install", help="把 agent-fw 安裝到 PATH")
    s.add_argument("--prefix", help="安裝前綴（預設 ~/.local）")
    s.set_defaults(func=_cmd_install)

    s = sub.add_parser("uninstall", help="從 PATH 移除")
    s.set_defaults(func=_cmd_uninstall)

    return p


# ---------------------------------------------------------------------------
# 子命令實作
# ---------------------------------------------------------------------------

def _resolve_root(args) -> Path:
    if getattr(args, "root", None):
        return Path(args.root).resolve()
    return core.find_framework_root()


def _cmd_init(args) -> int:
    """把當前目錄標記為 framework 根（複製必要檔案的提示）。"""
    cwd = Path.cwd()
    if (cwd / "VERSION").is_file():
        ui.warn(f"{cwd} 已經是 framework 根（VERSION 已存在）")
        return 0
    # 簡單起見，init 只是提示使用者從範本複製
    src = ROOT
    needed = ["VERSION", "CHANGELOG.md", "MIGRATION.md", "README.md", "INDEX.md", ".framework"]
    ui.header("Init Agent Framework")
    ui.info(f"framework 範本位於：{src}")
    ui.info(f"目標目錄：{cwd}")
    if not ui.prompt_yes_no(f"複製 {len(needed)} 個核心檔案/目錄到當前目錄？", default=True):
        ui.warn("已取消")
        return 0
    for name in needed:
        s = src / name
        d = cwd / name
        if d.exists():
            ui.info(f"跳過（已存在）：{name}")
            continue
        if s.is_dir():
            shutil.copytree(s, d)
        else:
            shutil.copy2(s, d)
        ui.success(f"複製：{name}")
    ui.success(f"初始化完成。下一步：agent-fw status")
    return 0


def _cmd_status(args) -> int:
    root = _resolve_root(args)
    manifest = version.get_current(root)
    det = detection.run_all(root)
    val = validate.run_all(root)

    ui.header("Framework Status")
    ui.subheader("版本")
    ui.kv("framework-version", str(manifest.version))
    ui.kv("schema-version", str(manifest.schema_version))
    ui.kv("last-updated", manifest.last_updated or "?")
    ui.kv("framework-status", manifest.framework_status)
    ui.kv("recommended-restart-on-bump", str(manifest.recommended_restart_on_bump))

    ui.subheader("健康度")
    overall = {"clean": ui.green("CLEAN"), "minor": ui.yellow("MINOR"), "major": ui.red("MAJOR")}[det.overall]
    ui.kv("detection", overall)
    if det.findings:
        for f in det.findings[:5]:
            ui.info(f"  · [{f.rule}] {f.severity}: {f.evidence[:80]}...")

    val_status = ui.green("OK") if val.failed == 0 else ui.red(f"{val.failed} failed")
    ui.kv("validation", val_status)
    ui.kv("  passed", str(val.passed))
    ui.kv("  warnings", str(val.warnings))
    ui.kv("  failed", str(val.failed))

    if det.overall == "major":
        ui.restart_warning(
            reason=f"detection 觸發：{', '.join(det.triggered)}",
            action="開新 session 並重跑 BOOTSTRAP",
            impact="繼續可能誤觸已廢棄規則",
        )
    return 0


def _cmd_read(args) -> int:
    root = _resolve_root(args)
    if args.path:
        p = (root / args.path).resolve()
        if not p.exists():
            ui.error(f"找不到：{p}")
            return 1
        print(core.read_text(p))
        return 0
    # 沒指定 path：照 PROTOCOL 順序輸出檔名清單
    order = [
        "VERSION",
        "CHANGELOG.md",
        ".framework/PROTOCOL.md",
        ".framework/BOOTSTRAP.md",
        ".framework/VERSION_AWARENESS.md",
        "INDEX.md",
    ]
    ui.header("Protocol Read Order")
    for i, rel in enumerate(order, 1):
        p = root / rel
        marker = ui.green("✓") if p.is_file() else ui.red("✗")
        ui.info(f"{i}. {marker} {rel}")
    return 0


def _cmd_bootstrap(args) -> int:
    root = _resolve_root(args)
    handoff_path = Path(args.handoff) if args.handoff else None
    rpt = bootstrap.run(
        root,
        last_known=args.last_known,
        handoff_path=handoff_path,
    )
    if args.format == "yaml":
        print(rpt.to_yaml())
    elif args.format == "json":
        import json
        print(json.dumps(rpt.to_dict(), indent=2, ensure_ascii=False))
    else:
        bootstrap.print_report(rpt)
    return 0 if rpt.ready_for_task else 2


def _cmd_bump(args) -> int:
    root = _resolve_root(args)
    breaking = [b.strip() for b in (args.breaking or "").split(",") if b.strip()]
    ui.header("Bumping framework version")
    ui.info(f"type: {args.type}")
    ui.info(f"reason: {args.reason}")
    if not ui.prompt_yes_no("確認執行？", default=True):
        ui.warn("已取消")
        return 0
    manifest = bump.run(
        root,
        bump_type=args.type,
        reason=args.reason,
        breaking_changes=breaking,
        notes=args.notes or "",
    )
    ui.success(f"新版本：{manifest.version}")
    ui.info("已更新：VERSION、CHANGELOG.md" + ("、MIGRATION.md" if args.type == "major" else ""))
    ui.info("建議下一步：跑 agent-fw validate 確認一致性")
    return 0


def _cmd_detect(args) -> int:
    root = _resolve_root(args)
    rpt = detection.run_all(root)
    if args.format == "json":
        import json
        print(json.dumps(rpt.to_dict(), indent=2, ensure_ascii=False))
    else:
        detection.print_report(rpt)
    return 0 if rpt.overall != "major" else 2


def _cmd_validate(args) -> int:
    root = _resolve_root(args)
    rpt = validate.run_all(root)
    validate.print_report(rpt)
    return 0 if rpt.failed == 0 else 1


def _cmd_handoff_new(args) -> int:
    root = _resolve_root(args)
    out = handoff.create(
        out_path=Path(args.out),
        framework_root=root,
        task_name=args.task,
        context_summary=args.summary,
        current_state=args.state,
        decisions=args.decisions,
        open_questions=args.questions,
        next_actions=args.next,
        loaded_frameworks=args.frameworks,
        from_session=args.from_session,
    )
    ui.success(f"handoff 已建立：{out}")
    ui.info("下一步建議：")
    ui.info("  1. 檢視並補完內容")
    ui.info(f"  2. 下一棒用 `agent-fw handoff validate {out}` 驗證")
    return 0


def _cmd_handoff_validate(args) -> int:
    root = _resolve_root(args)
    rpt = handoff.validate(Path(args.file), root)
    handoff.print_validation(rpt)
    return 0 if rpt.valid else 1


def _cmd_new_framework(args) -> int:
    root = _resolve_root(args)
    try:
        target = framework_new.create(root, args.slug, args.name, args.one_liner)
    except (ValueError, FileExistsError) as e:
        ui.error(str(e))
        return 1
    ui.success(f"新框架已建立：{target}")
    ui.info("檔案清單：")
    for f in sorted(target.iterdir()):
        ui.info(f"  · {f.name}")
    ui.info("下一步：")
    ui.info(f"  1. 編輯 {target.name}/FRAMEWORK.md（核心概念 / 操作步驟 / 反模式）")
    ui.info(f"  2. 編輯 {target.name}/META.md（相容性欄位）")
    ui.info(f"  3. 跑 `agent-fw validate` 檢查 INDEX 連結")
    return 0


def _cmd_prompt(args) -> int:
    root = _resolve_root(args)
    if args.output:
        out = prompt.write(root, target=args.target, output=Path(args.output), extra_context=args.extra)
        ui.success(f"system prompt 已寫入：{out}")
        ui.info("複製內容貼到 AI 工具的 system prompt 欄位即可。")
    else:
        text = prompt.generate(root, target=args.target, extra_context=args.extra)
        print(text)
    return 0


def _cmd_report(args) -> int:
    root = _resolve_root(args)
    out = report.generate(root, Path(args.output) if args.output else None)
    ui.success(f"儀表板已產生：{out}")
    if args.open:
        try:
            webbrowser.open(out.as_uri())
        except Exception as e:
            ui.warn(f"無法自動開啟：{e}")
            ui.info(f"手動開啟：file://{out}")
    return 0


def _cmd_tui(args) -> int:
    """互動式選單。"""
    try:
        root = _resolve_root(args)
    except FileNotFoundError as e:
        ui.error(str(e))
        ui.info("提示：在 framework 根目錄內執行，或用 --root 指定")
        return 1

    while True:
        ui.header(f"Agent Framework TUI — v{version.get_current(root).version}")
        choices = [
            "status — 顯示當前狀態",
            "bootstrap — 跑 session 啟動",
            "detect — 跑多版本混雜偵測",
            "validate — 驗證框架完整性",
            "bump — 版本 bump",
            "handoff new — 建立新 handoff",
            "new-framework — 建立新認知框架",
            "prompt — 產生 AI system prompt",
            "report — 產生 HTML 儀表板",
            "read — 顯示讀取協議順序",
            "exit",
        ]
        idx = ui.prompt_choice("選擇動作", choices)
        if idx is None or choices[idx].startswith("exit"):
            ui.info("Bye")
            return 0
        # 重新呼叫對應子命令
        cmd_map = {
            0: ["status"],
            1: ["bootstrap"],
            2: ["detect"],
            3: ["validate"],
            4: ["bump", "patch", "--reason", "(via TUI)"],
            5: ["handoff", "new", "--task", "tui-task", "--out", "./handoff-tui.md"],
            6: ["new-framework", "tui-new-fw"],
            7: ["prompt", "--for", "generic"],
            8: ["report", "--open"],
            9: ["read"],
        }
        sub = cmd_map.get(idx, [])
        if sub:
            try:
                main(["--root", str(root), *sub])
            except SystemExit:
                pass
        input(f"\n  {ui.gray('按 Enter 繼續...')}")


def _cmd_install(args) -> int:
    """把 agent-fw 與 agent_fw/ 安裝到 ~/.local/bin 或指定前綴。"""
    prefix = Path(args.prefix) if args.prefix else Path.home() / ".local"
    bin_dir = prefix / "bin"
    lib_dir = prefix / "share" / "agent-fw" / "agent_fw"

    bin_dir.mkdir(parents=True, exist_ok=True)
    lib_dir.mkdir(parents=True, exist_ok=True)

    # 複製 agent-fw
    src_bin = ROOT / "agent-fw"
    dst_bin = bin_dir / "agent-fw"
    shutil.copy2(src_bin, dst_bin)
    dst_bin.chmod(0o755)

    # 複製 agent_fw/ 套件
    src_pkg = ROOT / "agent_fw"
    for item in src_pkg.iterdir():
        s = item
        d = lib_dir / item.name
        if item.is_dir():
            if d.exists():
                shutil.rmtree(d)
            shutil.copytree(item, d)
        else:
            shutil.copy2(item, d)

    # 修正可執行檔內的 shebang 與路徑
    _patch_script(dst_bin, lib_dir.parent)

    # 提示 PATH
    ui.success(f"已安裝到：{dst_bin}")
    ui.info("套件路徑：" + str(lib_dir))
    path = os.environ.get("PATH", "")
    if str(bin_dir) not in path:
        ui.warn(f"{bin_dir} 不在 PATH 中，建議加到 ~/.bashrc / ~/.zshrc：")
        print(f"    export PATH=\"$HOME/.local/bin:$PATH\"")
    return 0


def _cmd_uninstall(args) -> int:
    prefix = Path.home() / ".local"
    for p in [prefix / "bin" / "agent-fw", prefix / "share" / "agent-fw"]:
        if p.is_file():
            p.unlink()
        elif p.is_dir():
            shutil.rmtree(p)
    ui.success("已移除 agent-fw（從 ~/.local）")
    return 0


def _patch_script(script_path: Path, real_lib_root: Path) -> None:
    """把 agent-fw 內的路徑改成真實安裝位置。"""
    text = script_path.read_text(encoding="utf-8")
    text = text.replace(
        f'HERE = Path(__file__).resolve().parent\nROOT = HERE.parent',
        f'HERE = Path(__file__).resolve().parent\nROOT = Path({str(real_lib_root)!r})',
    )
    script_path.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
