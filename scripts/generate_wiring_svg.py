#!/usr/bin/env python3
"""Generate the per-key matrix/GPIO wiring diagram."""

from __future__ import annotations

import html
import json
import re
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VIA_JSON = ROOT / "via" / "kinesis-dactyl-5x7.json"
OUTPUT = ROOT / "docs" / "wiring-layout.svg"

ROW_PINS = ("GP14", "GP15", "GP26", "GP27", "GP28", "GP29")
COL_PINS = ("GP2", "GP3", "GP4", "GP5", "GP6", "GP7", "GP8")

KEY_W = 90
KEY_H = 84
PITCH = 96


@dataclass(frozen=True)
class Key:
    qmk_row: int
    col: int
    x: int
    y: int
    height: int = KEY_H
    rotation: int = 0
    pivot_x: int = 0
    pivot_y: int = 0
    name: str = ""

    @property
    def side(self) -> str:
        return "L" if self.qmk_row < 6 else "R"

    @property
    def local_row(self) -> int:
        return self.qmk_row if self.qmk_row < 6 else self.qmk_row - 6


def main_keys() -> list[Key]:
    keys: list[Key] = []
    y_by_row = (100, 190, 280, 370, 460)

    left_cols = {
        0: range(0, 6),
        1: range(0, 6),
        2: range(0, 6),
        3: range(0, 6),
        4: range(0, 5),
    }
    for row, cols in left_cols.items():
        for col in cols:
            keys.append(Key(row, col, 60 + col * PITCH, y_by_row[row]))
    for qmk_row, visual_row in ((1, 0), (2, 1), (3, 2)):
        keys.append(Key(qmk_row, 6, 60 + 6 * PITCH, y_by_row[visual_row]))

    right_cols = {
        0: (5, 4, 3, 2, 1, 0),
        1: (5, 4, 3, 2, 1, 0),
        2: (5, 4, 3, 2, 1, 0),
        3: (5, 4, 3, 2, 1, 0),
        4: (4, 3, 2, 1, 0),
    }
    start_x = {0: 1146, 1: 1146, 2: 1146, 3: 1146, 4: 1242}
    for local_row, cols in right_cols.items():
        for index, col in enumerate(cols):
            keys.append(
                Key(6 + local_row, col, start_x[local_row] + index * PITCH, y_by_row[local_row])
            )
    for local_row, visual_row in ((1, 0), (2, 1), (3, 2)):
        keys.append(Key(6 + local_row, 6, 1050, y_by_row[visual_row]))

    return keys


def thumb_keys() -> list[Key]:
    left_rotation = {"rotation": 10, "pivot_x": 620, "pivot_y": 760}
    right_rotation = {"rotation": -10, "pivot_x": 1160, "pivot_y": 760}
    two_u = KEY_H * 2 + (PITCH - KEY_H)

    return [
        Key(5, 0, 576, 630, name="Ctrl", **left_rotation),
        Key(5, 2, 672, 630, name="Alt", **left_rotation),
        Key(5, 4, 480, 720, height=two_u, name="Backspace", **left_rotation),
        Key(5, 6, 576, 720, height=two_u, name="Delete", **left_rotation),
        Key(5, 1, 672, 720, name="Home", **left_rotation),
        Key(5, 5, 672, 810, name="End", **left_rotation),
        Key(11, 4, 1050, 630, name="GUI/Win", **right_rotation),
        Key(11, 2, 1146, 630, name="Ctrl", **right_rotation),
        Key(11, 6, 1050, 720, name="Page Up", **right_rotation),
        Key(11, 5, 1146, 720, height=two_u, name="Enter", **right_rotation),
        Key(11, 0, 1242, 720, height=two_u, name="Space", **right_rotation),
        Key(11, 1, 1050, 810, name="Page Down", **right_rotation),
    ]


def via_visible_coordinates() -> set[tuple[int, int]]:
    data = json.loads(VIA_JSON.read_text(encoding="utf-8"))
    coordinates: set[tuple[int, int]] = set()

    def visit(value: object) -> None:
        if isinstance(value, str):
            match = re.fullmatch(r"(\d+),(\d+)", value)
            if match:
                coordinates.add((int(match.group(1)), int(match.group(2))))
        elif isinstance(value, list):
            for item in value:
                visit(item)
        elif isinstance(value, dict):
            for item in value.values():
                visit(item)

    visit(data["layouts"]["keymap"])
    return coordinates


def key_svg(key: Key) -> str:
    side_class = "left" if key.side == "L" else "right"
    thumb_class = " thumb" if key.qmk_row in (5, 11) else ""
    transform = ""
    if key.rotation:
        transform = f' transform="rotate({key.rotation} {key.pivot_x} {key.pivot_y})"'

    center_x = key.x + KEY_W / 2
    if key.height > KEY_H:
        text_y = key.y + key.height / 2 - 23
    else:
        text_y = key.y + 22

    name = f" {key.name}" if key.name else ""
    meta = html.escape(f"{key.side}{name} · [{key.qmk_row},{key.col}]")
    matrix = f"R{key.local_row} C{key.col}"
    pins = f"{ROW_PINS[key.local_row]} / {COL_PINS[key.col]}"

    return f"""\
  <g class="key {side_class}{thumb_class}"{transform}>
    <rect class="key-shape" x="{key.x}" y="{key.y}" width="{KEY_W}" height="{key.height}" rx="9"/>
    <text class="key-meta" x="{center_x:g}" y="{text_y:g}">{meta}</text>
    <text class="key-matrix" x="{center_x:g}" y="{text_y + 22:g}">{matrix}</text>
    <text class="key-pins" x="{center_x:g}" y="{text_y + 42:g}">{pins}</text>
  </g>"""


def generate_svg(keys: list[Key]) -> str:
    key_markup = "\n".join(key_svg(key) for key in keys)
    return f"""\
<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="1750" height="1120" viewBox="0 0 1750 1120"
     role="img" aria-labelledby="title description">
  <title id="title">Kinesis Dactyl 5x7 每键矩阵与 GPIO 接线图</title>
  <desc id="description">76 个 VIA 可见键的本地矩阵行列、QMK 全局坐标以及行列 GPIO 引脚对。</desc>
  <style>
    :root {{
      color-scheme: dark;
    }}
    text {{
      font-family: Inter, "SF Pro Text", "PingFang SC", "Microsoft YaHei", sans-serif;
      fill: #e8edf5;
    }}
    .background {{
      fill: #171b22;
    }}
    .frame {{
      fill: #202630;
      stroke: #697386;
      stroke-width: 2;
    }}
    .key-shape {{
      fill: #303946;
      stroke: #79879a;
      stroke-width: 2;
    }}
    .left .key-shape {{
      fill: #263b4a;
      stroke: #6fa8c7;
    }}
    .right .key-shape {{
      fill: #3a304b;
      stroke: #a68ac7;
    }}
    .thumb .key-shape {{
      stroke-width: 3;
    }}
    .key-meta, .key-matrix, .key-pins {{
      text-anchor: middle;
      dominant-baseline: middle;
    }}
    .key-meta {{
      fill: #b8c2d1;
      font-size: 9px;
      font-weight: 500;
    }}
    .key-matrix {{
      fill: #ffffff;
      font-size: 15px;
      font-weight: 700;
    }}
    .key-pins {{
      fill: #ffd479;
      font-size: 11px;
      font-weight: 650;
    }}
    .title {{
      font-size: 30px;
      font-weight: 750;
    }}
    .subtitle {{
      fill: #bbc5d4;
      font-size: 14px;
    }}
    .section {{
      font-size: 17px;
      font-weight: 700;
    }}
    .legend {{
      fill: #c8d0dc;
      font-size: 14px;
    }}
    .warning {{
      fill: #ffce72;
      font-size: 14px;
      font-weight: 600;
    }}
    .left-label {{
      fill: #8dc9e8;
    }}
    .right-label {{
      fill: #c4a5e5;
    }}
  </style>

  <rect class="background" width="1750" height="1120"/>
  <rect class="frame" x="22" y="18" width="1706" height="1080" rx="24"/>

  <text class="title" x="60" y="55">Kinesis Dactyl 5x7 — 每键矩阵 / GPIO 接线图</text>
  <text class="subtitle" x="60" y="79">
    每键三行：侧与 QMK 全局坐标 / 本地 R-C / 行 GPIO 与列 GPIO。右半本地 R0–R5 在 QMK 中映射为全局行 6–11。
  </text>
  <text class="section left-label" x="60" y="94">左半</text>
  <text class="section right-label" x="1640" y="94" text-anchor="end">右半</text>

{key_markup}

  <g transform="translate(60 965)">
    <text class="section" x="0" y="0">引脚总表</text>
    <text class="legend" x="0" y="29">行：R0=GP14　R1=GP15　R2=GP26　R3=GP27　R4=GP28　R5=GP29</text>
    <text class="legend" x="0" y="55">列：C0=GP2　C1=GP3　C2=GP4　C3=GP5　C4=GP6　C5=GP7　C6=GP8</text>
    <text class="warning" x="0" y="86">COL2ROW：列 GPIO → 开关 → 二极管无环端 → 二极管带环端 → 行 GPIO</text>
  </g>

  <g transform="translate(930 965)">
    <text class="section" x="0" y="0">VIA 隐藏但实体保留的矩阵位置</text>
    <text class="legend" x="0" y="29">左：[0,6]、[4,5]、[4,6]、[5,3]</text>
    <text class="legend" x="0" y="55">右：[6,6]、[10,5]、[10,6]、[11,3]</text>
    <text class="warning" x="0" y="86">纵向 2u 仍然只使用一个开关和一个矩阵交点。</text>
  </g>
</svg>
"""


def main() -> None:
    keys = main_keys() + thumb_keys()
    generated_coordinates = {(key.qmk_row, key.col) for key in keys}
    visible_coordinates = via_visible_coordinates()

    if len(keys) != len(generated_coordinates):
        raise SystemExit("duplicate matrix coordinate in SVG layout")
    if generated_coordinates != visible_coordinates:
        missing = sorted(visible_coordinates - generated_coordinates)
        extra = sorted(generated_coordinates - visible_coordinates)
        raise SystemExit(f"SVG/VIA coordinate mismatch; missing={missing}, extra={extra}")

    OUTPUT.write_text(generate_svg(keys), encoding="utf-8")
    print(f"generated {OUTPUT.relative_to(ROOT)} with {len(keys)} visible keys")


if __name__ == "__main__":
    main()
