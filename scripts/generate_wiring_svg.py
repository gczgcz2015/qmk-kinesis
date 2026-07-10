#!/usr/bin/env python3
"""Generate the per-key matrix/GPIO wiring diagram."""

from __future__ import annotations

import html
import json
import math
import re
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VIAL_JSON = (
    ROOT
    / "keyboards"
    / "handwired"
    / "dactyl_manuform"
    / "5x7"
    / "keymaps"
    / "vial"
    / "vial.json"
)
KEYBOARD_JSON = ROOT / "keyboards" / "handwired" / "dactyl_manuform" / "5x7" / "keyboard.json"
KEYMAP_C = (
    ROOT
    / "keyboards"
    / "handwired"
    / "dactyl_manuform"
    / "5x7"
    / "keymaps"
    / "vial"
    / "keymap.c"
)
OUTPUT = ROOT / "docs" / "wiring-layout.svg"

ROW_PINS = ("GP14", "GP15", "GP26", "GP27", "GP9", "NO_PIN")
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
    for qmk_row, visual_row in ((0, 0), (1, 1), (2, 2)):
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
    for local_row, visual_row in ((0, 0), (1, 1), (2, 2)):
        keys.append(Key(6 + local_row, 6, 1050, y_by_row[visual_row]))

    return keys


def thumb_keys() -> list[Key]:
    return []


def joycon_layout_svg() -> str:
    return """\
  <g class="joycon-module" transform="rotate(10 640 780)">
    <rect class="joycon-body" x="520" y="660" width="250" height="220" rx="34"/>
    <circle class="joycon-stick-outer" cx="645" cy="750" r="64"/>
    <circle class="joycon-stick-inner" cx="645" cy="750" r="34"/>
    <text class="joycon-title" x="645" y="842">左侧 Joy-Con</text>
    <text class="joycon-note" x="645" y="862">GP28=X / GP29=Y</text>
  </g>
  <g class="joycon-module" transform="rotate(-10 1160 780)">
    <rect class="disabled-thumb-body" x="1035" y="660" width="250" height="220" rx="34"/>
    <text class="disabled-thumb-title" x="1160" y="746">右侧拇指区停用</text>
    <text class="disabled-thumb-note" x="1160" y="774">R5 = NO_PIN</text>
    <text class="disabled-thumb-note" x="1160" y="796">不安装开关 / 不接矩阵</text>
  </g>"""


def joycon_wiring_svg() -> str:
    return """\
  <g class="joycon-wiring" transform="translate(60 1660)">
    <text class="hardware-title" x="0" y="0">左侧 Joy-Con 接线</text>
    <text class="subtitle" x="0" y="26">Joy-Con 只接左侧主控；拇指区矩阵 R5 不接线。SW/BTN 暂不接。</text>

    <rect class="controller-body" x="0" y="62" width="360" height="250" rx="18"/>
    <text class="controller-title" x="180" y="94">左 RP2040-Zero</text>
    <text class="controller-note" x="180" y="118">只使用 3.3V 模拟输入，不能把 Joy-Con 接 5V</text>

    <g class="pin-list" transform="translate(42 146)">
      <circle class="pin-vcc" cx="0" cy="0" r="7"/><text class="pin-label" x="18" y="5">3V3</text>
      <circle class="pin-gnd" cx="0" cy="42" r="7"/><text class="pin-label" x="18" y="47">GND</text>
      <circle class="pin-x" cx="0" cy="84" r="7"/><text class="pin-label" x="18" y="89">GP28 / ADC2 / X</text>
      <circle class="pin-y" cx="0" cy="126" r="7"/><text class="pin-label" x="18" y="131">GP29 / ADC3 / Y</text>
    </g>

    <rect class="breakout-body" x="690" y="62" width="330" height="250" rx="18"/>
    <text class="controller-title" x="855" y="94">Joy-Con 5P FPC 转接板</text>
    <text class="controller-note" x="855" y="118">按你转接板丝印为准：VCC/GND/X/Y/SW</text>

    <g class="pin-list" transform="translate(740 146)">
      <circle class="pin-vcc" cx="0" cy="0" r="7"/><text class="pin-label" x="18" y="5">VCC</text>
      <circle class="pin-gnd" cx="0" cy="42" r="7"/><text class="pin-label" x="18" y="47">GND</text>
      <circle class="pin-x" cx="0" cy="84" r="7"/><text class="pin-label" x="18" y="89">X / VRX</text>
      <circle class="pin-y" cx="0" cy="126" r="7"/><text class="pin-label" x="18" y="131">Y / VRY</text>
      <circle class="pin-unused" cx="0" cy="168" r="7"/><text class="pin-label muted" x="18" y="173">SW / BTN 不接</text>
    </g>

    <path class="wire-vcc" d="M42 146 C260 120, 520 120, 740 146"/>
    <path class="wire-gnd" d="M42 188 C260 176, 520 176, 740 188"/>
    <path class="wire-x" d="M42 230 C260 232, 520 232, 740 230"/>
    <path class="wire-y" d="M42 272 C260 288, 520 288, 740 272"/>

    <rect class="wasd-box" x="1110" y="62" width="520" height="250" rx="18"/>
    <text class="controller-title" x="1370" y="94">固件映射</text>
    <text class="controller-note" x="1370" y="122">X 轴：左=A，右=D；Y 轴：上=W，下=S</text>
    <text class="controller-note" x="1370" y="150">支持斜向：左上=A+W，右下=D+S</text>
    <text class="controller-note" x="1370" y="178">上电静置约 1 秒：32 个稳定样本自动校准中心</text>
    <text class="controller-note" x="1370" y="204">按下阈值 ±110，释放阈值 ±70，带低通滤波和滞回</text>
    <text class="controller-warning" x="1370" y="238">如果方向相反，先改 keymap.c 的轴方向逻辑，不要改到 5V。</text>
  </g>"""


def vial_visible_coordinates() -> set[tuple[int, int]]:
    data = json.loads(VIAL_JSON.read_text(encoding="utf-8"))
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


def base_keycodes() -> dict[tuple[int, int], str]:
    keyboard = json.loads(KEYBOARD_JSON.read_text(encoding="utf-8"))
    layout = keyboard["layouts"]["LAYOUT_5x7"]["layout"]
    coordinates = [tuple(item["matrix"]) for item in layout]

    source = re.sub(r"//.*", "", KEYMAP_C.read_text(encoding="utf-8"))
    marker = "[_BASE] = LAYOUT_5x7("
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
            f"LAYOUT_5x7/base key count mismatch: {len(coordinates)} coordinates, "
            f"{len(arguments)} keycodes"
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
        "TG(_KEYPAD)": "Keypad",
        "MO(_FN)": "Fn",
        "MO(_NAV_MEDIA)": "Nav/Media",
        "XXXXXXX": "Disabled",
    }
    if keycode in labels:
        return labels[keycode]
    if keycode.startswith("KC_") and len(keycode) == 4:
        return keycode[-1]
    return keycode


def key_svg(key: Key, keycodes: dict[tuple[int, int], str]) -> str:
    side_class = "left" if key.side == "L" else "right"
    thumb_class = " thumb" if key.qmk_row in (5, 11) else ""
    transform = ""
    if key.rotation:
        transform = f' transform="rotate({key.rotation} {key.pivot_x} {key.pivot_y})"'

    center_x = key.x + KEY_W / 2
    if key.height > KEY_H:
        text_y = key.y + key.height / 2 - 30
    else:
        text_y = key.y + 16

    label = html.escape(keycode_label(keycodes[(key.qmk_row, key.col)]))
    meta = html.escape(f"{key.side} · [{key.qmk_row},{key.col}]")
    matrix = f"R{key.local_row} C{key.col}"
    pins = f"{ROW_PINS[key.local_row]} / {COL_PINS[key.col]}"

    return f"""\
  <g class="key {side_class}{thumb_class}"{transform}>
    <rect class="key-shape" x="{key.x}" y="{key.y}" width="{KEY_W}" height="{key.height}" rx="9"/>
    <text class="key-label" x="{center_x:g}" y="{text_y:g}">{label}</text>
    <text class="key-meta" x="{center_x:g}" y="{text_y + 18:g}">{meta}</text>
    <text class="key-matrix" x="{center_x:g}" y="{text_y + 37:g}">{matrix}</text>
    <text class="key-pins" x="{center_x:g}" y="{text_y + 56:g}">{pins}</text>
  </g>"""


def rotate_point(x: float, y: float, angle: int, pivot_x: float, pivot_y: float) -> tuple[float, float]:
    if not angle:
        return x, y
    radians = math.radians(angle)
    dx = x - pivot_x
    dy = y - pivot_y
    return (
        pivot_x + dx * math.cos(radians) - dy * math.sin(radians),
        pivot_y + dx * math.sin(radians) + dy * math.cos(radians),
    )


def wiring_points(key: Key, offset_y: int) -> tuple[tuple[float, float], tuple[float, float]]:
    center_x = key.x + KEY_W / 2
    center_y = key.y + offset_y + key.height / 2
    pivot_y = key.pivot_y + offset_y
    col_point = rotate_point(
        center_x - 28, center_y, key.rotation, key.pivot_x, pivot_y
    )
    row_point = rotate_point(
        center_x + 31, center_y, key.rotation, key.pivot_x, pivot_y
    )
    return col_point, row_point


def wiring_key_shape_svg(key: Key, offset_y: int) -> str:
    y = key.y + offset_y
    transform = ""
    if key.rotation:
        transform = (
            f' transform="rotate({key.rotation} {key.pivot_x} {key.pivot_y + offset_y})"'
        )
    return (
        f'  <g class="wiring-key"{transform}>\n'
        f'    <rect class="wiring-key-shape" x="{key.x}" y="{y}" '
        f'width="{KEY_W}" height="{key.height}" rx="9"/>\n'
        f"  </g>"
    )


def wiring_key_component_svg(key: Key, offset_y: int) -> str:
    center_x = key.x + KEY_W / 2
    center_y = key.y + offset_y + key.height / 2
    transform = ""
    if key.rotation:
        transform = (
            f' transform="rotate({key.rotation} {key.pivot_x} {key.pivot_y + offset_y})"'
        )

    return f"""\
  <g class="wiring-component"{transform}>
    <line class="component-col-wire" x1="{center_x - 28:g}" y1="{center_y:g}" x2="{center_x - 15:g}" y2="{center_y:g}"/>
    <rect class="wiring-switch" x="{center_x - 15:g}" y="{center_y - 9:g}" width="22" height="18" rx="3"/>
    <line class="component-wire" x1="{center_x + 7:g}" y1="{center_y:g}" x2="{center_x + 11:g}" y2="{center_y:g}"/>
    <rect class="wiring-diode" x="{center_x + 11:g}" y="{center_y - 7:g}" width="16" height="14" rx="7"/>
    <rect class="wiring-diode-band" x="{center_x + 22:g}" y="{center_y - 7:g}" width="4" height="14"/>
    <line class="component-row-wire" x1="{center_x + 27:g}" y1="{center_y:g}" x2="{center_x + 31:g}" y2="{center_y:g}"/>
    <circle class="col-junction" cx="{center_x - 28:g}" cy="{center_y:g}" r="4"/>
    <circle class="row-junction" cx="{center_x + 31:g}" cy="{center_y:g}" r="4"/>
  </g>"""


def wiring_overlay_svg(keys: list[Key], offset_y: int) -> str:
    parts = [wiring_key_shape_svg(key, offset_y) for key in keys]

    for side in ("L", "R"):
        side_keys = [key for key in keys if key.side == side]
        for col in range(7):
            points = [
                wiring_points(key, offset_y)[0] for key in side_keys if key.col == col
            ]
            points.sort(key=lambda point: (point[1], point[0]))
            point_text = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
            parts.append(f'  <polyline class="wiring-col-line" points="{point_text}"/>')
            for x, y in points:
                parts.append(f'  <circle class="col-junction" cx="{x:.1f}" cy="{y:.1f}" r="4"/>')
            label_x, label_y = points[0]
            parts.append(
                f'  <text class="wiring-col-label" x="{label_x:.1f}" '
                f'y="{label_y - 55:.1f}">C{col}</text>'
            )

        for local_row in range(5):
            points = [
                wiring_points(key, offset_y)[1]
                for key in side_keys
                if key.local_row == local_row
            ]
            points.sort(key=lambda point: point[0])
            point_text = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
            parts.append(f'  <polyline class="wiring-row-halo" points="{point_text}"/>')
            row_class = "wiring-row-line wiring-thumb-row" if local_row == 5 else "wiring-row-line"
            parts.append(f'  <polyline class="{row_class}" points="{point_text}"/>')
            for x, y in points:
                parts.append(f'  <circle class="row-junction" cx="{x:.1f}" cy="{y:.1f}" r="4"/>')
            label_x, label_y = points[0]
            label = f"R{local_row}"
            parts.append(
                f'  <text class="wiring-row-label" x="{label_x - 85:.1f}" '
                f'y="{label_y - 14:.1f}">{label}</text>'
            )

    parts.extend(wiring_key_component_svg(key, offset_y) for key in keys)
    return "\n".join(parts)


def generate_svg(keys: list[Key], keycodes: dict[tuple[int, int], str]) -> str:
    key_markup = "\n".join(key_svg(key, keycodes) for key in keys)
    wiring_markup = wiring_overlay_svg(keys, 1150)
    joycon_markup = joycon_layout_svg()
    joycon_wiring_markup = joycon_wiring_svg()
    return f"""\
<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="1750" height="2220" viewBox="0 0 1750 2220"
     role="img" aria-labelledby="title description">
  <title id="title">Kinesis Dactyl 5x7 Joy-Con 分支第一层键位、矩阵、GPIO 与接线图</title>
  <desc id="description">64 个 Vial 可见主键的第一层键位、矩阵坐标、GPIO 引脚对，以及每侧行列总线、二极管方向和左侧 Joy-Con 接线。</desc>
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
    .joycon-body {{
      fill: #3c3836;
      stroke: #d65d0e;
      stroke-width: 4;
    }}
    .joycon-stick-outer {{
      fill: #504945;
      stroke: #fabd2f;
      stroke-width: 4;
    }}
    .joycon-stick-inner {{
      fill: #282828;
      stroke: #ebdbb2;
      stroke-width: 3;
    }}
    .joycon-title, .disabled-thumb-title {{
      text-anchor: middle;
      dominant-baseline: middle;
      font-size: 17px;
      font-weight: 800;
    }}
    .joycon-title {{
      fill: #fabd2f;
    }}
    .joycon-note, .disabled-thumb-note {{
      text-anchor: middle;
      dominant-baseline: middle;
      font-size: 12px;
      font-weight: 650;
    }}
    .joycon-note {{
      fill: #ebdbb2;
    }}
    .disabled-thumb-body {{
      fill: #2a2f38;
      stroke: #928374;
      stroke-width: 3;
      stroke-dasharray: 10 8;
    }}
    .disabled-thumb-title {{
      fill: #d5c4a1;
    }}
    .disabled-thumb-note {{
      fill: #a89984;
    }}
    .key-label, .key-meta, .key-matrix, .key-pins {{
      text-anchor: middle;
      dominant-baseline: middle;
    }}
    .key-label {{
      fill: #ffffff;
      font-size: 14px;
      font-weight: 750;
    }}
    .key-meta {{
      fill: #b8c2d1;
      font-size: 8px;
      font-weight: 500;
    }}
    .key-matrix {{
      fill: #dce5f1;
      font-size: 13px;
      font-weight: 700;
    }}
    .key-pins {{
      fill: #ffd479;
      font-size: 10px;
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
    .divider {{
      stroke: #566174;
      stroke-width: 2;
    }}
    .hardware-title {{
      font-size: 25px;
      font-weight: 750;
    }}
    .wiring-key-shape {{
      fill: #252d38;
      stroke: #68778b;
      stroke-width: 2;
    }}
    .wiring-col-line {{
      fill: none;
      stroke: #e4b85f;
      stroke-width: 4;
      stroke-linejoin: round;
      stroke-linecap: round;
    }}
    .wiring-row-halo {{
      fill: none;
      stroke: #202630;
      stroke-width: 11;
      stroke-linejoin: round;
      stroke-linecap: round;
    }}
    .wiring-row-line {{
      fill: none;
      stroke: #6fb7df;
      stroke-width: 5;
      stroke-linejoin: round;
      stroke-linecap: round;
    }}
    .wiring-thumb-row {{
      stroke: #67d8ff;
      stroke-width: 7;
    }}
    .wiring-col-label {{
      fill: #ffd479;
      font-size: 15px;
      font-weight: 700;
      text-anchor: middle;
      paint-order: stroke;
      stroke: #202630;
      stroke-width: 6px;
    }}
    .wiring-row-label {{
      fill: #9bddf7;
      font-size: 14px;
      font-weight: 700;
      text-anchor: end;
      paint-order: stroke;
      stroke: #202630;
      stroke-width: 6px;
    }}
    .component-col-wire {{
      stroke: #e4b85f;
      stroke-width: 3;
    }}
    .component-row-wire {{
      stroke: #6fb7df;
      stroke-width: 3;
    }}
    .component-wire {{
      stroke: #d5deea;
      stroke-width: 2;
    }}
    .wiring-switch {{
      fill: #3a4554;
      stroke: #e2e8f0;
      stroke-width: 2;
    }}
    .wiring-diode {{
      fill: #e09c4d;
      stroke: #ffca78;
      stroke-width: 1;
    }}
    .wiring-diode-band {{
      fill: #11151b;
    }}
    .col-junction {{
      fill: #ffd479;
      stroke: #202630;
      stroke-width: 1;
    }}
    .row-junction {{
      fill: #8bd0f4;
      stroke: #202630;
      stroke-width: 1;
    }}
    .wiring-legend-box {{
      fill: #252d39;
      stroke: #68778b;
      stroke-width: 2;
    }}
    .legend-col-line {{
      stroke: #e4b85f;
      stroke-width: 5;
    }}
    .legend-row-line {{
      stroke: #67d8ff;
      stroke-width: 7;
    }}
    .legend-diode {{
      fill: #e09c4d;
      stroke: #ffca78;
      stroke-width: 2;
    }}
    .legend-diode-band {{
      fill: #11151b;
    }}
    .wiring-note {{
      fill: #c3cedc;
      font-size: 14px;
    }}
    .wiring-emphasis {{
      fill: #ffd479;
      font-size: 16px;
      font-weight: 750;
    }}
    .left-label {{
      fill: #8dc9e8;
    }}
    .right-label {{
      fill: #c4a5e5;
    }}
    .controller-body, .breakout-body, .wasd-box {{
      fill: #252d39;
      stroke: #68778b;
      stroke-width: 2;
    }}
    .controller-title {{
      fill: #ebdbb2;
      font-size: 18px;
      font-weight: 800;
      text-anchor: middle;
    }}
    .controller-note {{
      fill: #c3cedc;
      font-size: 14px;
      text-anchor: middle;
    }}
    .controller-warning {{
      fill: #fabd2f;
      font-size: 14px;
      font-weight: 750;
      text-anchor: middle;
    }}
    .pin-label {{
      fill: #ebdbb2;
      font-size: 14px;
      font-weight: 700;
    }}
    .muted {{
      fill: #928374;
    }}
    .pin-vcc {{
      fill: #cc241d;
    }}
    .pin-gnd {{
      fill: #3c3836;
      stroke: #ebdbb2;
      stroke-width: 1.5;
    }}
    .pin-x {{
      fill: #98971a;
    }}
    .pin-y {{
      fill: #458588;
    }}
    .pin-unused {{
      fill: #928374;
    }}
    .wire-vcc, .wire-gnd, .wire-x, .wire-y {{
      fill: none;
      stroke-width: 5;
      stroke-linecap: round;
    }}
    .wire-vcc {{
      stroke: #cc241d;
    }}
    .wire-gnd {{
      stroke: #3c3836;
    }}
    .wire-x {{
      stroke: #98971a;
    }}
    .wire-y {{
      stroke: #458588;
    }}
  </style>

  <rect class="background" width="1750" height="2220"/>
  <rect class="frame" x="22" y="18" width="1706" height="2180" rx="24"/>

  <text class="title" x="60" y="55">Kinesis Dactyl 5x7 Joy-Con — 第一层键位 / 矩阵 / GPIO 接线图</text>
  <text class="subtitle" x="60" y="79">
    每键四行：第一层键位 / 侧与 QMK 全局坐标 / 本地 R-C / 行 GPIO 与列 GPIO。拇指区矩阵隐藏，左侧改接 Joy-Con。
  </text>
  <text class="section left-label" x="60" y="94">左半</text>
  <text class="section right-label" x="1640" y="94" text-anchor="end">右半</text>

{key_markup}
{joycon_markup}

  <g transform="translate(60 965)">
    <text class="section" x="0" y="0">引脚总表</text>
    <text class="legend" x="0" y="29">行：R0=GP14　R1=GP15　R2=GP26　R3=GP27　R4=GP9　R5=NO_PIN（拇指区停用）</text>
    <text class="legend" x="0" y="55">列：C0=GP2　C1=GP3　C2=GP4　C3=GP5　C4=GP6　C5=GP7　C6=GP8</text>
    <text class="warning" x="0" y="86">COL2ROW：列 GPIO → 开关 → 二极管无环端 → 二极管带环端 → 行 GPIO；Joy-Con：X=GP28，Y=GP29</text>
  </g>

  <g transform="translate(930 965)">
    <text class="section" x="0" y="0">QMK 保留、Vial 隐藏且无需接线的位置</text>
    <text class="legend" x="0" y="29">左：[3,6]、[4,5]、[4,6]、整行 [5,0]–[5,6]</text>
    <text class="legend" x="0" y="55">右：[9,6]、[10,5]、[10,6]、整行 [11,0]–[11,6]</text>
    <text class="warning" x="0" y="86">R4 已从 GP28 改到 GP9；GP28/GP29 专用于左侧 Joy-Con ADC。</text>
  </g>

  <line class="divider" x1="60" y1="1128" x2="1690" y2="1128"/>
  <text class="hardware-title" x="60" y="1172">按实际键位连接行线与列线</text>
  <text class="subtitle" x="60" y="1198">
    下图与上方主键区几何 1:1；拇指区不接矩阵。键帽内仅画开关与二极管。黄色连接同一列，蓝色连接同一行。
  </text>

{wiring_markup}
{joycon_wiring_markup}

  <rect class="wiring-legend-box" x="60" y="2090" width="1630" height="82" rx="14"/>
  <line class="legend-col-line" x1="90" y1="2121" x2="145" y2="2121"/>
  <text class="wiring-note" x="158" y="2126">黄色：同一列 C0–C6 相连</text>
  <line class="legend-row-line" x1="400" y1="2121" x2="455" y2="2121"/>
  <text class="wiring-note" x="468" y="2126">蓝色：同一行 R0–R4 相连</text>
  <rect class="legend-diode" x="740" y="2108" width="46" height="24" rx="12"/>
  <rect class="legend-diode-band" x="776" y="2108" width="7" height="24"/>
  <text class="wiring-note" x="798" y="2126">黑色带环端接蓝色行线</text>
  <text class="wiring-emphasis" x="90" y="2158">R4 改接 GP9；左侧 Joy-Con：VCC→3V3，GND→GND，X→GP28，Y→GP29，SW/BTN 不接。</text>
  <text class="wiring-note" x="1210" y="2158">行列线交叉处绝缘，不直接相连。</text>
</svg>
"""


def main() -> None:
    keys = main_keys() + thumb_keys()
    keycodes = base_keycodes()
    generated_coordinates = {(key.qmk_row, key.col) for key in keys}
    visible_coordinates = vial_visible_coordinates()

    if len(keys) != len(generated_coordinates):
        raise SystemExit("duplicate matrix coordinate in SVG layout")
    if generated_coordinates != visible_coordinates:
        missing = sorted(visible_coordinates - generated_coordinates)
        extra = sorted(generated_coordinates - visible_coordinates)
        raise SystemExit(f"SVG/Vial coordinate mismatch; missing={missing}, extra={extra}")
    if not generated_coordinates.issubset(keycodes):
        missing = sorted(generated_coordinates - keycodes.keys())
        raise SystemExit(f"missing base-layer keycodes for SVG coordinates: {missing}")

    OUTPUT.write_text(generate_svg(keys, keycodes), encoding="utf-8")
    print(f"generated {OUTPUT.relative_to(ROOT)} with {len(keys)} visible keys")


if __name__ == "__main__":
    main()
