#!/usr/bin/env python3
"""Generate the 81-key matrix, GPIO, split-power, and PMW3360 wiring diagram."""

from __future__ import annotations

import html
import json
import re
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
KEYBOARD_DIR = ROOT / "keyboards/handwired/dactyl_manuform/5x7"
KEYBOARD_JSON = KEYBOARD_DIR / "keyboard.json"
VIAL_JSON = KEYBOARD_DIR / "keymaps/vial/vial.json"
KEYMAP_C = KEYBOARD_DIR / "keymaps/vial/keymap.c"
OUTPUT = ROOT / "docs/wiring-layout.svg"

ROW_PINS = ("GP14", "GP15", "GP26", "GP27", "GP28", "GP29")
LEFT_COL_PINS = ("GP2", "GP3", "GP4", "GP5", "GP6", "GP7", "GP8", "NO_PIN", "NO_PIN")
RIGHT_COL_PINS = ("GP2", "GP3", "GP4", "GP5", "GP6", "GP7", "GP8", "GP9", "GP10")
LAYOUT_NAME = "LAYOUT_5x7_5x9"

KEY_W = 78
KEY_H = 70
PITCH = 84
LEFT_X = 60
RIGHT_X = 1120
ROW_Y = (130, 208, 286, 364, 442)


@dataclass(frozen=True)
class Key:
    qmk_row: int
    col: int
    x: int
    y: int
    height: int = KEY_H

    @property
    def side(self) -> str:
        return "L" if self.qmk_row < 6 else "R"

    @property
    def local_row(self) -> int:
        return self.qmk_row if self.qmk_row < 6 else self.qmk_row - 6

    @property
    def col_pin(self) -> str:
        pins = LEFT_COL_PINS if self.side == "L" else RIGHT_COL_PINS
        return pins[self.col]


def main_keys() -> list[Key]:
    keys: list[Key] = []

    left_by_row = {
        0: range(7),
        1: range(7),
        2: range(7),
        3: range(6),
        4: range(5),
    }
    for row, cols in left_by_row.items():
        for col in cols:
            keys.append(Key(row, col, LEFT_X + col * PITCH, ROW_Y[row]))

    right_by_row = {
        0: range(9),
        1: range(9),
        2: (0, 3, 4, 5, 6, 7, 8),
        3: (0, 3, 4, 5, 6, 7, 8),
        4: (4, 5, 6, 7, 8),
    }
    for row, cols in right_by_row.items():
        for col in cols:
            keys.append(Key(6 + row, col, RIGHT_X + col * PITCH, ROW_Y[row]))

    return keys


def thumb_keys() -> list[Key]:
    two_u = KEY_H * 2 + (PITCH - KEY_H)
    return [
        Key(5, 4, 480, 590),
        Key(5, 6, 564, 590),
        Key(5, 1, 396, 668, height=two_u),
        Key(5, 2, 480, 668, height=two_u),
        Key(5, 5, 564, 668),
        Key(5, 3, 564, 746),
        Key(11, 6, 1120, 590),
        Key(11, 4, 1204, 590),
        Key(11, 5, 1120, 668),
        Key(11, 2, 1204, 668, height=two_u),
        Key(11, 1, 1288, 668, height=two_u),
        Key(11, 3, 1120, 746),
    ]


def vial_visible_coordinates() -> set[tuple[int, int]]:
    data = json.loads(VIAL_JSON.read_text(encoding="utf-8"))
    coordinates: set[tuple[int, int]] = set()

    def visit(value: object) -> None:
        if isinstance(value, str):
            if match := re.fullmatch(r"(\d+),(\d+)", value):
                coordinates.add((int(match.group(1)), int(match.group(2))))
        elif isinstance(value, list):
            for item in value:
                visit(item)
        elif isinstance(value, dict):
            for item in value.values():
                visit(item)

    visit(data["layouts"]["keymap"])
    return coordinates


def base_keycodes() -> dict[tuple[int, int], str]:
    keyboard = json.loads(KEYBOARD_JSON.read_text(encoding="utf-8"))
    layout = keyboard["layouts"][LAYOUT_NAME]["layout"]
    coordinates = [tuple(item["matrix"]) for item in layout]

    source = re.sub(r"//.*", "", KEYMAP_C.read_text(encoding="utf-8"))
    marker = f"[_BASE] = {LAYOUT_NAME}("
    start = source.index(marker) + len(marker)
    depth = 1
    token: list[str] = []
    arguments: list[str] = []

    for char in source[start:]:
        if char == "(":
            depth += 1
            token.append(char)
        elif char == ")":
            depth -= 1
            if depth == 0:
                arguments.append("".join(token).strip())
                break
            token.append(char)
        elif char == "," and depth == 1:
            arguments.append("".join(token).strip())
            token = []
        else:
            token.append(char)

    if len(coordinates) != len(arguments):
        raise SystemExit(
            f"{LAYOUT_NAME}/base key count mismatch: "
            f"{len(coordinates)} coordinates, {len(arguments)} keycodes"
        )
    return dict(zip(coordinates, arguments))


def keycode_label(keycode: str) -> str:
    labels = {
        "KC_EQL": "=",
        "KC_MINS": "-",
        "KC_TAB": "Tab",
        "KC_ESC": "Esc",
        "KC_LSFT": "L Shift",
        "KC_RSFT": "R Shift",
        "KC_GRV": "`",
        "KC_CAPS": "Caps",
        "KC_LEFT": "←",
        "KC_RGHT": "→",
        "KC_UP": "↑",
        "KC_DOWN": "↓",
        "KC_BSLS": "\\",
        "KC_SCLN": ";",
        "KC_QUOT": "'",
        "KC_COMM": ",",
        "KC_DOT": ".",
        "KC_SLSH": "/",
        "KC_LBRC": "[",
        "KC_RBRC": "]",
        "KC_LCTL": "L Ctrl",
        "KC_RCTL": "R Ctrl",
        "KC_BSPC": "Backspace",
        "KC_LALT": "L Alt",
        "KC_DEL": "Delete",
        "KC_HOME": "Home",
        "KC_END": "End",
        "KC_RGUI": "GUI/Win",
        "KC_SPC": "Space",
        "KC_PGUP": "Page Up",
        "KC_ENT": "Enter",
        "KC_PGDN": "Page Down",
        "KC_BTN1": "Mouse Left",
        "KC_BTN2": "Mouse Right",
        "KC_BTN3": "Mouse Middle",
        "PMW_CPI_DN": "CPI−",
        "PMW_CPI_UP": "CPI+",
        "TG(_KEYPAD)": "Keypad",
        "MO(_FN)": "Fn",
        "MO(_NAV_MEDIA)": "Nav/Media",
    }
    if keycode in labels:
        return labels[keycode]
    if keycode.startswith("KC_") and len(keycode) == 4:
        return keycode[-1]
    return keycode


def key_svg(key: Key, keycodes: dict[tuple[int, int], str]) -> str:
    center_x = key.x + KEY_W / 2
    text_y = key.y + (key.height / 2 - 24 if key.height > KEY_H else 14)
    label = html.escape(keycode_label(keycodes[(key.qmk_row, key.col)]))
    metadata = html.escape(f"{key.side} [{key.qmk_row},{key.col}]")
    pins = html.escape(f"R{key.local_row} {ROW_PINS[key.local_row]} / C{key.col} {key.col_pin}")
    return f"""\
  <g class="key {key.side.lower()}{" thumb" if key.local_row == 5 else ""}">
    <rect x="{key.x}" y="{key.y}" width="{KEY_W}" height="{key.height}" rx="8"/>
    <text class="key-label" x="{center_x}" y="{text_y}">{label}</text>
    <text class="key-meta" x="{center_x}" y="{text_y + 18}">{metadata}</text>
    <text class="key-pins" x="{center_x}" y="{text_y + 36}">{pins}</text>
  </g>"""


def wiring_point(key: Key, offset_y: int) -> tuple[tuple[float, float], tuple[float, float]]:
    center_y = key.y + offset_y + key.height / 2
    return (key.x + 17, center_y), (key.x + KEY_W - 17, center_y)


def wiring_svg(keys: list[Key], offset_y: int) -> str:
    parts: list[str] = []
    for key in keys:
        parts.append(
            f'  <rect class="wiring-key" x="{key.x}" y="{key.y + offset_y}" '
            f'width="{KEY_W}" height="{key.height}" rx="8"/>'
        )

    for side in ("L", "R"):
        side_keys = [key for key in keys if key.side == side]
        for col in sorted({key.col for key in side_keys}):
            points = sorted(
                (wiring_point(key, offset_y)[0] for key in side_keys if key.col == col),
                key=lambda point: (point[1], point[0]),
            )
            point_text = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
            parts.append(f'  <polyline class="col-line" points="{point_text}"/>')
            x, y = points[0]
            parts.append(f'  <text class="col-label" x="{x}" y="{y - 42}">C{col}</text>')

        for row in range(6):
            points = sorted(
                (wiring_point(key, offset_y)[1] for key in side_keys if key.local_row == row),
                key=lambda point: point[0],
            )
            point_text = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
            parts.append(
                f'  <polyline class="row-line{" thumb-row" if row == 5 else ""}" '
                f'points="{point_text}"/>'
            )
            x, y = points[0]
            parts.append(
                f'  <text class="row-label" x="{x - 48}" y="{y - 10}">'
                f'R{row} · {ROW_PINS[row]}</text>'
            )

    for key in keys:
        col_point, row_point = wiring_point(key, offset_y)
        center_x = key.x + KEY_W / 2
        center_y = key.y + offset_y + key.height / 2
        parts.append(f"""\
  <g class="component">
    <line class="component-col" x1="{col_point[0]}" y1="{col_point[1]}" x2="{center_x - 12}" y2="{center_y}"/>
    <rect class="switch" x="{center_x - 12}" y="{center_y - 8}" width="20" height="16" rx="2"/>
    <line class="component-wire" x1="{center_x + 8}" y1="{center_y}" x2="{center_x + 13}" y2="{center_y}"/>
    <rect class="diode" x="{center_x + 13}" y="{center_y - 7}" width="17" height="14" rx="6"/>
    <rect class="diode-band" x="{center_x + 25}" y="{center_y - 7}" width="4" height="14"/>
    <line class="component-row" x1="{center_x + 30}" y1="{center_y}" x2="{row_point[0]}" y2="{row_point[1]}"/>
  </g>""")

    return "\n".join(parts)


def hardware_svg() -> str:
    return """\
  <g transform="translate(60 2020)">
    <rect class="hardware-box" x="0" y="0" width="610" height="300" rx="16"/>
    <text class="hardware-title" x="24" y="35">右侧 YD-RP2040（USB 主端）</text>
    <text class="hardware-text" x="24" y="70">矩阵：C0–C8 → GP2–GP10</text>
    <text class="hardware-text" x="24" y="96">矩阵：R0–R5 → GP14, GP15, GP26–GP29</text>
    <text class="hardware-text" x="24" y="122">分体数据：GP0 → TRS Tip</text>
    <text class="hardware-text" x="24" y="148">分体供电：Vout → TRS Ring</text>
    <text class="hardware-text" x="24" y="184">PMW3360：SCL→GP18　MOS→GP19</text>
    <text class="hardware-text" x="24" y="210">　　　　　MIS→GP20　SS→GP21</text>
    <text class="hardware-text" x="24" y="236">　　　　　VCC→3V3　GND→GND</text>
    <text class="warning" x="24" y="270">Ogen MOT/RES 不接；VCC 绝对不要接 5V。</text>

    <rect class="hardware-box" x="650" y="0" width="560" height="300" rx="16"/>
    <text class="hardware-title" x="674" y="35">左侧 YD-RP2040（从端）</text>
    <text class="hardware-text" x="674" y="70">矩阵：C0–C6 → GP2–GP8</text>
    <text class="hardware-text" x="674" y="96">逻辑 C7/C8 → NO_PIN，不接线</text>
    <text class="hardware-text" x="674" y="122">矩阵：R0–R5 → GP14, GP15, GP26–GP29</text>
    <text class="hardware-text" x="674" y="148">分体数据：TRS Tip → GP0</text>
    <text class="hardware-text" x="674" y="174">分体供电：TRS Ring → Vin</text>
    <text class="hardware-text" x="674" y="210">正常使用不连接左侧 USB-C。</text>
    <text class="warning" x="674" y="270">两侧都断电后才能插拔 TRS。</text>

    <rect class="hardware-box" x="1250" y="0" width="690" height="300" rx="16"/>
    <text class="hardware-title" x="1274" y="35">三芯 TRS 与固件行为</text>
    <text class="hardware-text" x="1274" y="70">Tip：右 GP0 ↔ 左 GP0（PIO 半双工数据）</text>
    <text class="hardware-text" x="1274" y="96">Ring：右 Vout → 左 Vin（右侧供电）</text>
    <text class="hardware-text" x="1274" y="122">Sleeve：右 GND ↔ 左 GND</text>
    <text class="hardware-text" x="1274" y="158">CPI 档位：100 / 200 / 400 / 800 / 1200 / 1600 / 2400 / 3200</text>
    <text class="hardware-text" x="1274" y="184">CPI− / CPI+ 可在 Vial User 页分配，档位断电保存。</text>
    <text class="hardware-text" x="1274" y="210">Ogen 丝印 UP 朝键盘顶部；只输出光标 X/Y。</text>
    <text class="warning" x="1274" y="270">只把右侧 USB-C 接到电脑；禁止双 USB 供电。</text>
  </g>"""


def generate_svg(keys: list[Key], keycodes: dict[tuple[int, int], str]) -> str:
    key_markup = "\n".join(key_svg(key, keycodes) for key in keys)
    wiring_markup = wiring_svg(keys, 1000)
    return f"""\
<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="2050" height="2380" viewBox="0 0 2050 2380"
     role="img" aria-labelledby="title description">
  <title id="title">Kinesis Dactyl 5x7+5x9 YD-RP2040 接线图</title>
  <desc id="description">81 个 Vial 可见键、非对称 12×9 分体矩阵、右侧 PMW3360、TRS 数据与供电接线。</desc>
  <style>
    text {{ font-family: Inter, "PingFang SC", "Microsoft YaHei", sans-serif; fill: #e8edf5; }}
    .background {{ fill: #171b22; }}
    .frame {{ fill: #202630; stroke: #697386; stroke-width: 2; }}
    .title {{ font-size: 28px; font-weight: 800; }}
    .subtitle {{ fill: #bbc5d4; font-size: 14px; }}
    .section {{ font-size: 18px; font-weight: 800; }}
    .left-label {{ fill: #8dc9e8; }}
    .right-label {{ fill: #c4a5e5; }}
    .key rect {{ fill: #303946; stroke: #79879a; stroke-width: 2; }}
    .key.left rect {{ fill: #263b4a; stroke: #6fa8c7; }}
    .key.right rect {{ fill: #3a304b; stroke: #a68ac7; }}
    .key.thumb rect {{ stroke-width: 3; }}
    .key-label, .key-meta, .key-pins {{ text-anchor: middle; dominant-baseline: middle; }}
    .key-label {{ fill: #fff; font-size: 12px; font-weight: 750; }}
    .key-meta {{ fill: #b8c2d1; font-size: 8px; }}
    .key-pins {{ fill: #ffd479; font-size: 8px; font-weight: 650; }}
    .trackball {{ fill: #3c3836; stroke: #fabd2f; stroke-width: 4; }}
    .trackball-inner {{ fill: #282828; stroke: #ebdbb2; stroke-width: 3; }}
    .trackball-text {{ fill: #fabd2f; font-size: 14px; font-weight: 750; text-anchor: middle; }}
    .summary-box, .hardware-box {{ fill: #252d39; stroke: #68778b; stroke-width: 2; }}
    .summary {{ fill: #c8d0dc; font-size: 13px; }}
    .wiring-key {{ fill: #252d38; stroke: #68778b; stroke-width: 2; }}
    .col-line {{ fill: none; stroke: #e4b85f; stroke-width: 4; stroke-linejoin: round; }}
    .row-line {{ fill: none; stroke: #6fb7df; stroke-width: 5; stroke-linejoin: round; }}
    .thumb-row {{ stroke: #67d8ff; stroke-width: 7; }}
    .col-label {{ fill: #ffd479; font-size: 13px; font-weight: 700; text-anchor: middle; }}
    .row-label {{ fill: #9bddf7; font-size: 12px; font-weight: 700; text-anchor: end; }}
    .component-col {{ stroke: #e4b85f; stroke-width: 3; }}
    .component-row {{ stroke: #6fb7df; stroke-width: 3; }}
    .component-wire {{ stroke: #d5deea; stroke-width: 2; }}
    .switch {{ fill: #3a4554; stroke: #e2e8f0; stroke-width: 2; }}
    .diode {{ fill: #e09c4d; stroke: #ffca78; }}
    .diode-band {{ fill: #11151b; }}
    .hardware-title {{ fill: #fff; font-size: 18px; font-weight: 800; }}
    .hardware-text {{ fill: #cbd5e1; font-size: 14px; }}
    .warning {{ fill: #ffce72; font-size: 14px; font-weight: 700; }}
  </style>

  <rect class="background" width="2050" height="2380"/>
  <rect class="frame" x="20" y="18" width="2010" height="2342" rx="24"/>
  <text class="title" x="60" y="55">Kinesis Dactyl 5x7+5x9 — YD-RP2040 / 右主端 / PMW3360</text>
  <text class="subtitle" x="60" y="80">每键显示：默认键位、全局矩阵坐标、本地行列及 GPIO。二极管方向为 COL2ROW（带环端接行线）。</text>
  <text class="section left-label" x="60" y="112">左半：32 主键 + 6 拇指键</text>
  <text class="section right-label" x="1120" y="112">右半：37 主键 + 6 拇指键 + 轨迹球</text>

{key_markup}

  <g>
    <circle class="trackball" cx="1660" cy="690" r="92"/>
    <circle class="trackball-inner" cx="1660" cy="690" r="62"/>
    <text class="trackball-text" x="1660" y="800">右侧 Ogen Lite / PMW3360</text>
    <text class="trackball-text" x="1660" y="822">UP 朝键盘顶部 · SPI0 GP18–GP21</text>
  </g>

  <rect class="summary-box" x="60" y="875" width="1930" height="100" rx="14"/>
  <text class="summary" x="84" y="908">左列：C0–C6=GP2–GP8；C7/C8=NO_PIN　　右列：C0–C8=GP2–GP10</text>
  <text class="summary" x="84" y="936">两侧行：R0=GP14　R1=GP15　R2=GP26　R3=GP27　R4=GP28　R5（拇指）=GP29</text>
  <text class="warning" x="84" y="962">右主端：USB-C → 右 YD-RP2040；TRS Tip=GP0，Ring=右 Vout→左 Vin，Sleeve=GND。禁止带电插拔。</text>

  <text class="section" x="60" y="1015">逐键矩阵接线：黄色为列，蓝色为行；开关 → 二极管无环端 → 带环端 → 行线</text>
{wiring_markup}

{hardware_svg()}
</svg>
"""


def main() -> None:
    keys = main_keys() + thumb_keys()
    generated_coordinates = {(key.qmk_row, key.col) for key in keys}
    visible_coordinates = vial_visible_coordinates()
    keycodes = base_keycodes()

    if len(keys) != 81 or len(generated_coordinates) != 81:
        raise SystemExit("SVG layout must contain 81 unique keys")
    if generated_coordinates != visible_coordinates:
        missing = sorted(visible_coordinates - generated_coordinates)
        extra = sorted(generated_coordinates - visible_coordinates)
        raise SystemExit(f"SVG/Vial coordinate mismatch; missing={missing}, extra={extra}")
    if not generated_coordinates <= keycodes.keys():
        missing = sorted(generated_coordinates - keycodes.keys())
        raise SystemExit(f"missing base-layer keycodes: {missing}")

    OUTPUT.write_text(generate_svg(keys, keycodes), encoding="utf-8")
    print(f"generated {OUTPUT.relative_to(ROOT)} with {len(keys)} visible keys")


if __name__ == "__main__":
    main()
