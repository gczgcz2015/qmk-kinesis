#!/usr/bin/env python3
"""Generate the split 4x6+3 keymap and RP2040-Zero wiring diagram."""

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

ROW_PINS = ("GP14", "GP15", "GP26", "GP27", "GP8")
COL_PINS = ("GP2", "GP3", "GP4", "GP5", "GP6", "GP7")
LAYOUT_NAME = "LAYOUT_split_4x6_3"

KEY_W = 100
KEY_H = 68
KEY_PITCH_X = 110
KEY_PITCH_Y = 82
LEFT_KEY_X = 70
RIGHT_KEY_X = 1040
KEY_Y = 150


@dataclass(frozen=True)
class Key:
    side: str
    local_row: int
    col: int
    x: int
    y: int

    @property
    def qmk_row(self) -> int:
        return self.local_row if self.side == "L" else 5 + self.local_row


def main_keys() -> list[Key]:
    keys: list[Key] = []
    for side, base_x in (("L", LEFT_KEY_X), ("R", RIGHT_KEY_X)):
        for row in range(4):
            for col in range(6):
                keys.append(
                    Key(side, row, col, base_x + col * KEY_PITCH_X, KEY_Y + row * KEY_PITCH_Y)
                )

    thumb_y = KEY_Y + 4 * KEY_PITCH_Y + 28
    for col in (3, 4, 5):
        keys.append(Key("L", 4, col, LEFT_KEY_X + col * KEY_PITCH_X, thumb_y))
    for col in (0, 1, 2):
        keys.append(Key("R", 4, col, RIGHT_KEY_X + col * KEY_PITCH_X, thumb_y))
    return keys


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
        "KC_TAB": "Tab",
        "KC_ESC": "Esc",
        "KC_LSFT": "L Shift",
        "KC_LCTL": "L Ctrl",
        "KC_BSPC": "Backspace",
        "KC_MINS": "-",
        "KC_BSLS": "\\",
        "KC_SCLN": ";",
        "KC_QUOT": "'",
        "KC_COMM": ",",
        "KC_DOT": ".",
        "KC_SLSH": "/",
        "KC_RSFT": "R Shift",
        "KC_ENT": "Enter",
        "KC_SPC": "Space",
        "MO(_FN)": "Fn",
        "MO(_NAV_MEDIA)": "Nav/Mouse",
    }
    if keycode in labels:
        return labels[keycode]
    if keycode.startswith("KC_") and len(keycode) == 4:
        return keycode[-1]
    return keycode


def rgb_chain(keys: list[Key], side: str) -> list[Key]:
    by_coordinate = {
        (key.local_row, key.col): key for key in keys if key.side == side
    }
    chain: list[Key] = []
    for row in range(5):
        columns = range(6) if row % 2 == 0 else range(5, -1, -1)
        chain.extend(
            by_coordinate[(row, col)]
            for col in columns
            if (row, col) in by_coordinate
        )
    return chain


def top_key_svg(key: Key, keycode: str) -> str:
    center = key.x + KEY_W / 2
    return f"""\
  <g class="key">
    <rect x="{key.x}" y="{key.y}" width="{KEY_W}" height="{KEY_H}" rx="11"/>
    <text class="key-label" x="{center:g}" y="{key.y + 25}">{html.escape(keycode_label(keycode))}</text>
    <text class="key-meta" x="{center:g}" y="{key.y + 45}">{key.side} R{key.local_row}C{key.col} · QMK {key.qmk_row},{key.col}</text>
    <text class="key-pin" x="{center:g}" y="{key.y + 61}">{ROW_PINS[key.local_row]} / {COL_PINS[key.col]}</text>
  </g>"""


def wiring_geometry(key: Key) -> tuple[int, int]:
    panel_x = 70 if key.side == "L" else 950
    x = panel_x + 95 + key.col * 108
    y = 795 + key.local_row * 96
    return x, y


def wiring_bus_svg(keys: list[Key], side: str) -> str:
    parts: list[str] = []
    side_keys = [key for key in keys if key.side == side]
    panel_x = 70 if side == "L" else 950

    for row, pin in enumerate(ROW_PINS):
        row_keys = [key for key in side_keys if key.local_row == row]
        starts = [wiring_geometry(key)[0] for key in row_keys]
        y = wiring_geometry(row_keys[0])[1] + 31
        parts.append(
            f'<path class="row-wire" d="M{min(starts) - 28} {y} H{max(starts) + 92}"/>'
        )
        parts.append(
            f'<text class="row-label" x="{min(starts) - 34}" y="{y + 5}">R{row} · {pin}</text>'
        )

    for col, pin in enumerate(COL_PINS):
        col_keys = [key for key in side_keys if key.col == col]
        x = wiring_geometry(col_keys[0])[0] + 78
        ys = [wiring_geometry(key)[1] + 31 for key in col_keys]
        parts.append(
            f'<path class="col-wire" d="M{x} {min(ys) - 30} V{max(ys) + 20}"/>'
        )
        parts.append(
            f'<text class="col-label" x="{x}" y="{min(ys) - 39}">C{col} · {pin}</text>'
        )

    parts.append(
        f'<text class="panel-caption" x="{panel_x + 400}" y="1320">'
        f'{"左" if side == "L" else "右"}侧：蓝色 R 总线 / 黄色 C 总线；交叉处必须绝缘</text>'
    )
    return "\n".join(parts)


def wiring_key_svg(key: Key, led_index: int) -> str:
    x, y = wiring_geometry(key)
    return f"""\
  <g class="pcb">
    <rect x="{x}" y="{y}" width="92" height="62" rx="14"/>
    <circle class="rgb-pad" cx="{x + 12}" cy="{y + 12}" r="5"/>
    <circle class="row-pad" cx="{x + 17}" cy="{y + 31}" r="7"/>
    <circle class="col-pad" cx="{x + 75}" cy="{y + 31}" r="7"/>
    <rect class="switch" x="{x + 34}" y="{y + 20}" width="24" height="23" rx="4"/>
    <text class="pad-letter" x="{x + 17}" y="{y + 35}">R</text>
    <text class="pad-letter" x="{x + 75}" y="{y + 35}">C</text>
    <text class="pcb-index" x="{x + 46}" y="{y + 56}">{key.side}R{key.local_row}C{key.col} · LED{led_index}</text>
  </g>"""


def rgb_wiring_svg(keys: list[Key], side: str, start_index: int) -> str:
    chain = rgb_chain(keys, side)
    parts: list[str] = []
    first_x, first_y = wiring_geometry(chain[0])
    parts.append(
        f'<path class="rgb-wire" d="M{first_x - 42} {first_y + 12} H{first_x + 12}"/>'
    )
    parts.append(
        f'<text class="rgb-label" x="{first_x - 46}" y="{first_y + 17}">GP1 → LED{start_index}.I</text>'
    )
    for current, following in zip(chain, chain[1:]):
        x1, y1 = wiring_geometry(current)
        x2, y2 = wiring_geometry(following)
        parts.append(
            f'<path class="rgb-wire" d="M{x1 + 82} {y1 + 12} C{x1 + 98} {y1 + 12}, '
            f'{x2 - 6} {y2 + 12}, {x2 + 12} {y2 + 12}"/>'
        )
    return "\n".join(parts)


def generate_svg(keys: list[Key], keycodes: dict[tuple[int, int], str]) -> str:
    top_keys = "\n".join(
        top_key_svg(key, keycodes[(key.qmk_row, key.col)]) for key in keys
    )
    led_indices: dict[tuple[int, int], int] = {}
    for side, start in (("L", 0), ("R", 27)):
        for offset, key in enumerate(rgb_chain(keys, side)):
            led_indices[(key.qmk_row, key.col)] = start + offset

    wiring = "\n".join(
        [wiring_bus_svg(keys, "L"), wiring_bus_svg(keys, "R")]
        + [
            wiring_key_svg(key, led_indices[(key.qmk_row, key.col)])
            for key in keys
        ]
        + [rgb_wiring_svg(keys, "L", 0), rgb_wiring_svg(keys, "R", 27)]
    )

    return f"""\
<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="1800" height="2100" viewBox="0 0 1800 2100"
     role="img" aria-labelledby="title description">
  <title id="title">分体 4x6+3 与 PMW3360 接线图</title>
  <desc id="description">两块 RP2040-Zero、每侧 27 键 ROW2COL 矩阵与独立 SK6812 灯链；右手 PMW3360，GP0 单线分体通信。</desc>
  <style>
    text {{ font-family: Inter, "SF Pro Text", "PingFang SC", "Microsoft YaHei", sans-serif; fill: #edf2f8; }}
    .bg {{ fill: #131821; }}
    .panel {{ fill: #202837; stroke: #56647a; stroke-width: 2; }}
    .title {{ font-size: 32px; font-weight: 800; }}
    .subtitle {{ fill: #bac7d9; font-size: 16px; }}
    .section {{ font-size: 22px; font-weight: 800; }}
    .key rect {{ fill: #293b4c; stroke: #73b9df; stroke-width: 2; }}
    .key-label {{ font-size: 17px; font-weight: 800; text-anchor: middle; }}
    .key-meta {{ fill: #bfd7e8; font-size: 10px; font-weight: 700; text-anchor: middle; }}
    .key-pin {{ fill: #ffd47b; font-size: 10px; font-weight: 700; text-anchor: middle; }}
    .side-title {{ font-size: 19px; font-weight: 800; text-anchor: middle; }}
    .warning {{ fill: #ffd47b; font-size: 15px; font-weight: 750; }}
    .note {{ fill: #c7d1df; font-size: 14px; }}
    .row-wire {{ fill: none; stroke: #63bde9; stroke-width: 6; stroke-linecap: round; opacity: .85; }}
    .col-wire {{ fill: none; stroke: #e5b34f; stroke-width: 5; stroke-linecap: round; opacity: .85; }}
    .rgb-wire {{ fill: none; stroke: #c485dc; stroke-width: 3; stroke-linecap: round; opacity: .9; }}
    .row-label {{ fill: #9bdcff; font-size: 11px; font-weight: 800; text-anchor: end; }}
    .col-label {{ fill: #ffd47b; font-size: 11px; font-weight: 800; text-anchor: middle; }}
    .rgb-label {{ fill: #e6b5f5; font-size: 10px; font-weight: 800; text-anchor: end; }}
    .pcb rect:first-child {{ fill: #373141; stroke: #aa8ec5; stroke-width: 1.5; }}
    .row-pad {{ fill: #63bde9; }}
    .col-pad {{ fill: #e5b34f; }}
    .rgb-pad {{ fill: #c485dc; }}
    .switch {{ fill: #596475; stroke: #e2e9f1; stroke-width: 1; }}
    .pad-letter {{ fill: #151922; font-size: 9px; font-weight: 900; text-anchor: middle; }}
    .pcb-index {{ fill: #c1cad6; font-size: 8px; text-anchor: middle; }}
    .panel-caption {{ fill: #c7d1df; font-size: 13px; text-anchor: middle; }}
    .controller {{ fill: #252e3d; stroke: #7a899f; stroke-width: 2; }}
    .controller-title {{ font-size: 21px; font-weight: 800; }}
    .pin {{ font-size: 14px; font-weight: 700; }}
    .pin-accent {{ fill: #ffd47b; }}
    .trackball {{ fill: #273945; stroke: #77c7d9; stroke-width: 3; }}
    .trs {{ stroke: #8fe0b0; stroke-width: 7; fill: none; stroke-linecap: round; }}
  </style>

  <rect class="bg" width="1800" height="2100"/>
  <rect class="panel" x="24" y="20" width="1752" height="2055" rx="24"/>
  <text class="title" x="60" y="64">RP2040-Zero 分体 4×6 + 3 · PMW3360 轨迹球</text>
  <text class="subtitle" x="60" y="92">每侧 27 键 · ROW2COL · 左手 USB 主控 · 右手轨迹球 · GP0 半双工分体 · 每侧 GP1 独立 27 灯链</text>

  <text class="section" x="60" y="128">第一层键位、矩阵坐标与 GPIO</text>
  <text class="side-title" x="400" y="140">左手</text>
  <text class="side-title" x="1370" y="140">右手</text>
{top_keys}
  <text class="warning" x="60" y="590">Plum Twist D1：固件为 ROW2COL；焊接面观察时条纹 K 朝中央开关孔。R 接蓝色行线，C 接黄色列线。</text>
  <text class="note" x="60" y="616">拇指区复用第 5 行：左手 R4C3–C5，右手 R4C0–C2。每侧矩阵仍只需 5 行 + 6 列。</text>

  <line x1="60" y1="650" x2="1740" y2="650" stroke="#56647a" stroke-width="2"/>
  <text class="section" x="60" y="688">两侧 27 块 Plum Twist PCB：行列总线与 RGB 蛇形顺序</text>
  <rect class="panel" x="55" y="710" width="825" height="650" rx="18"/>
  <rect class="panel" x="930" y="710" width="815" height="650" rx="18"/>
  <text class="side-title" x="467" y="748">左侧 LED0–26</text>
  <text class="side-title" x="1337" y="748">右侧 LED27–53</text>
{wiring}

  <line x1="60" y1="1388" x2="1740" y2="1388" stroke="#56647a" stroke-width="2"/>
  <text class="section" x="60" y="1428">RP2040-Zero 引脚与外设</text>
  <rect class="controller" x="60" y="1450" width="800" height="465" rx="20"/>
  <text class="controller-title" x="90" y="1490">左手 · USB 主控</text>
  <text class="pin" x="90" y="1530">矩阵行：R0–R4 → GP14 / GP15 / GP26 / GP27 / GP8</text>
  <text class="pin" x="90" y="1560">矩阵列：C0–C5 → GP2 / GP3 / GP4 / GP5 / GP6 / GP7</text>
  <text class="pin" x="90" y="1590">RGB：GP1 → 220–470 Ω → LED0.I；27 颗 + 接 3V3，− 接 GND</text>
  <text class="pin pin-accent" x="90" y="1620">TRS DATA：GP0；Ring：5V；Sleeve：GND</text>
  <text class="pin" x="90" y="1680">空闲 GPIO：GP9 / GP10 / GP11 / GP12 / GP13 / GP28 / GP29</text>
  <text class="note" x="90" y="1720">左手不连接摇杆或轨迹球；GP8 只作为拇指区矩阵行 R4。</text>

  <rect class="controller" x="940" y="1450" width="800" height="465" rx="20"/>
  <text class="controller-title" x="970" y="1490">右手 · PMW3360 轨迹球</text>
  <text class="pin" x="970" y="1530">矩阵行：R0–R4 → GP14 / GP15 / GP26 / GP27 / GP8</text>
  <text class="pin" x="970" y="1560">矩阵列：C0–C5 → GP2 / GP3 / GP4 / GP5 / GP6 / GP7</text>
  <text class="pin" x="970" y="1590">RGB：GP1 → 220–470 Ω → LED27.I；27 颗 + 接 3V3，− 接 GND</text>
  <text class="pin pin-accent" x="970" y="1620">TRS DATA：GP0；Ring：5V；Sleeve：GND</text>
  <rect class="trackball" x="980" y="1660" width="205" height="150" rx="25"/>
  <circle class="trackball" cx="1082" cy="1715" r="47"/>
  <text class="pin" x="1025" y="1790">Ogen / PMW3360</text>
  <text class="pin pin-accent" x="1230" y="1670">CS → GP9</text>
  <text class="pin pin-accent" x="1230" y="1700">SCLK → GP10</text>
  <text class="pin pin-accent" x="1230" y="1730">MOSI → GP11</text>
  <text class="pin pin-accent" x="1230" y="1760">MISO → GP12</text>
  <text class="pin" x="1230" y="1790">GP13 → 预留，不连接</text>
  <text class="pin" x="1230" y="1820">VCC → 3V3；GND → GND</text>
  <text class="note" x="970" y="1860">SPI1；默认 1600 CPI。Fn + 右拇指前两键调节 CPI− / CPI+。</text>

  <path class="trs" d="M390 1960 H1410"/>
  <circle cx="390" cy="1960" r="12" fill="#8fe0b0"/>
  <circle cx="1410" cy="1960" r="12" fill="#8fe0b0"/>
  <text class="side-title" x="900" y="1948">TRS：Tip GP0 ↔ GP0 · Ring 5V ↔ 5V · Sleeve GND ↔ GND</text>
  <text class="warning" x="170" y="2010">必须完全断电后插拔 TRS；连接完成后只给左手接 USB。两侧刷入同一个 UF2。</text>
  <text class="note" x="170" y="2040">PMW3360 必须使用匹配透镜并移除传感器/透镜上的运输保护膜；VCC 与所有 GPIO 均为 3.3 V。</text>
</svg>
"""


def main() -> None:
    keys = main_keys()
    keycodes = base_keycodes()
    generated_coordinates = {(key.qmk_row, key.col) for key in keys}
    visible_coordinates = vial_visible_coordinates()

    if len(keys) != 54 or len(generated_coordinates) != 54:
        raise SystemExit("SVG layout must contain 54 unique keys")
    if generated_coordinates != visible_coordinates:
        missing = sorted(visible_coordinates - generated_coordinates)
        extra = sorted(generated_coordinates - visible_coordinates)
        raise SystemExit(f"SVG/Vial coordinate mismatch; missing={missing}, extra={extra}")

    OUTPUT.write_text(generate_svg(keys, keycodes), encoding="utf-8")
    print(f"generated {OUTPUT.relative_to(ROOT)} with {len(keys)} visible keys")


if __name__ == "__main__":
    main()
