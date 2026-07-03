#!/usr/bin/env python3
"""Render D2 (.d2) source files to SVG/PNG/PDF with professional defaults.

Usage:
    python render.py diagram.d2                       # -> diagram.svg
    python render.py diagram.d2 --png                 # -> diagram.png
    python render.py diagram.d2 --format pdf          # -> diagram.pdf
    python render.py diagram.d2 --animate 1400        # animated SVG (multi-board)
    python render.py diagram.d2 --theme 4 --layout elk --pad 60
    python render.py *.d2 --png                       # batch render

Defaults (applied unless overridden by --flags or vars.d2-config in the source):
    theme-id:      4        (Cool classics - modern, corporate-friendly)
    dark-theme-id: (unset)  (only set when the source or --dark_theme explicitly opts in)
    layout-engine: elk      (cleaner orthogonal routing than default dagre)
    pad:           60       (tighter than the 100 default; slide-friendly)

The script checks d2's EXIT STATUS, not output-file existence, because D2
may write a partial render on error. It also strips CLI flags that conflict
with the chosen output format (e.g. --animate-interval on PNG/PDF).
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

D2_BIN = shutil.which("d2") or "d2"

# Defaults -- mirrors the SKILL.md "professional defaults" section.
# NOTE: DEFAULT_DARK_THEME is intentionally empty. Setting --dark-theme (even to 200)
# bakes a prefers-color-scheme:dark CSS switch into the SVG, which silently recolors
# the diagram under OS dark mode. Only opt in via the source's d2-config or --dark_theme.
DEFAULT_THEME = "4"
DEFAULT_DARK_THEME = ""
DEFAULT_LAYOUT = "elk"
DEFAULT_PAD = "60"


def parse_d2_config(source: str) -> dict[str, str]:
    """Extract vars.d2-config.* keys from a .d2 source so the CLI flags match
    what the file declares. We only look for the keys that matter for rendering;
    nested braces are tracked very loosely (good enough for typical d2-config blocks).
    """
    config: dict[str, str] = {}
    m = re.search(r"vars\s*:\s*\{[^{}]*d2-config\s*:\s*\{", source, re.DOTALL)
    if not m:
        return config
    start = m.end()
    depth = 1
    i = start
    while i < len(source) and depth > 0:
        if source[i] == "{":
            depth += 1
        elif source[i] == "}":
            depth -= 1
        i += 1
    body = source[start : i - 1]

    key_map = {
        "theme-id": "theme",
        "dark-theme-id": "dark-theme",
        "layout-engine": "layout",
        "pad": "pad",
        "sketch": "sketch",
    }
    for src_key, cli_key in key_map.items():
        km = re.search(rf"\b{re.escape(src_key)}\s*:\s*([^\n;]+)", body)
        if km:
            value = km.group(1)
            # Strip trailing `# ...` comments (outside quotes) and whitespace.
            # Hex colors must be quoted in D2, so an unquoted `#` always starts
            # a comment.
            if "#" in value and not value.strip().startswith('"'):
                value = value.split("#", 1)[0]
            value = value.strip().strip('"').strip("'").strip()
            config[cli_key] = value
    return config


def build_d2_command(
    src: Path,
    dst: Path,
    file_config: dict[str, str],
    args: argparse.Namespace,
) -> list[str]:
    """Assemble the d2 CLI invocation."""
    cmd: list[str] = [D2_BIN]

    def add(flag: str, value: str | None, file_key: str, default_val: str):
        chosen = value or file_config.get(file_key, "") or default_val
        if chosen and chosen.lower() not in ("", "false", "0", "-1"):
            cmd.extend([f"--{flag}", chosen])

    if not args.force_flags:
        add("theme", args.theme, "theme", DEFAULT_THEME)
        add("dark-theme", args.dark_theme, "dark-theme", DEFAULT_DARK_THEME)
        add("layout", args.layout, "layout", DEFAULT_LAYOUT)
        add("pad", args.pad, "pad", DEFAULT_PAD)

    if args.sketch:
        cmd.append("--sketch")

    fmt = dst.suffix.lstrip(".").lower()
    if args.animate and fmt in ("svg", "gif"):
        cmd.extend(["--animate-interval", str(args.animate)])

    cmd.extend([str(src), str(dst)])
    return cmd


def render_one(src: Path, args: argparse.Namespace) -> int:
    if not src.exists():
        print(f"error: input file not found: {src}", file=sys.stderr)
        return 2

    source = src.read_text(encoding="utf-8")
    file_config = parse_d2_config(source)

    ext = "png" if args.png else args.format
    dst = src.with_suffix(f".{ext}")
    if args.output and len(args.inputs) == 1:
        dst = Path(args.output)

    cmd = build_d2_command(src, dst, file_config, args)

    if args.verbose:
        print("[render] " + " ".join(cmd), file=sys.stderr)

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
    except FileNotFoundError:
        print(
            f"error: d2 executable not found at '{D2_BIN}'. "
            "Install from https://d2lang.com.",
            file=sys.stderr,
        )
        return 127

    if result.returncode != 0:
        # D2 may have written a partial file on error -- remove it so the
        # caller doesn't mistake it for success.
        if dst.exists():
            dst.unlink()
        sys.stderr.write(result.stderr or result.stdout or "unknown d2 error\n")
        print(f"error: d2 exited with status {result.returncode}", file=sys.stderr)
        return result.returncode

    print(f"  {src} -> {dst}")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(
        description="Render D2 diagrams with professional defaults.",
        usage="python render.py [options] file1.d2 [file2.d2 ...]",
    )
    p.add_argument("inputs", nargs="+", type=Path, help=".d2 source file(s)")
    p.add_argument("-o", "--output", help="output path (single-file mode only)")
    p.add_argument(
        "--format",
        default="svg",
        choices=["svg", "png", "pdf", "gif", "pptx", "txt"],
        help="output format (default: svg)",
    )
    p.add_argument("--png", action="store_true", help="shortcut for --format png")
    p.add_argument("--theme", help="theme id (overrides file's d2-config)")
    p.add_argument("--dark_theme", dest="dark_theme", help="dark theme id (SVG only)")
    p.add_argument("--layout", help="layout engine: dagre | elk | tala")
    p.add_argument("--pad", help="padding in pixels")
    p.add_argument("--sketch", action="store_true", help="hand-drawn aesthetic")
    p.add_argument("--animate", type=int, help="animate multi-board (ms; SVG/GIF only)")
    p.add_argument(
        "--force-flags",
        action="store_true",
        help="ignore theme/layout/pad in the source's d2-config; use only CLI flags",
    )
    p.add_argument("-v", "--verbose", action="store_true", help="echo the d2 command")
    args = p.parse_args()

    if args.output and len(args.inputs) > 1:
        p.error("--output can only be used with a single input file")

    rc = 0
    for src in args.inputs:
        rc = max(rc, render_one(src, args))
    return rc


if __name__ == "__main__":
    sys.exit(main())
