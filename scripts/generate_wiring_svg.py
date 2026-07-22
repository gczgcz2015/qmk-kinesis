#!/usr/bin/env python3
"""Generate the standalone left-hand Plum Twist wiring diagram."""

from __future__ import annotations

import html
import json
import re
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
KEYBOARD_DIR = ROOT / "keyboards/handwired/dactyl_manuform/5x7"
VIAL_JSON = KEYBOARD_DIR / "keymaps/vial/vial.json"
KEYBOARD_JSON = KEYBOARD_DIR / "keyboard.json"
KEYMAP_C = KEYBOARD_DIR / "keymaps/vial/keymap.c"
OUTPUT = ROOT / "docs/wiring-layout.svg"

ROW_PINS = ("GP14", "GP15", "GP26", "GP27", "GP9")
COL_PINS = ("GP2", "GP3", "GP4", "GP5", "GP6", "GP7")

KEY_W = 132
KEY_H = 84
KEY_GAP = 14
KEY_X = 70
KEY_Y = 148


@dataclass(frozen=True)
class Key:
    qmk_row: int
    col: int
    x: int
    y: int


def main_keys() -> list[Key]:
    return [
        Key(row, col, KEY_X + col * (KEY_W + KEY_GAP), KEY_Y + row * (KEY_H + KEY_GAP))
        for row in range(5)
        for col in range(6)
        if (row, col) != (4, 5)
    ]


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
    layout = keyboard["layouts"]["LAYOUT_5x6"]["layout"]
    coordinates = [tuple(item["matrix"]) for item in layout]

    source = re.sub(r"//.*", "", KEYMAP_C.read_text(encoding="utf-8"))
    marker = "[_BASE] = LAYOUT_5x6("
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
            f"LAYOUT_5x6/base key count mismatch: {len(coordinates)} coordinates, "
            f"{len(arguments)} keycodes"
        )
    return dict(zip(coordinates, arguments))


def keycode_label(keycode: str) -> str:
    labels = {
        "KC_EQL": "=",
        "KC_TAB": "Tab",
        "KC_ESC": "Esc",
        "KC_LSFT": "L Shift",
        "KC_GRV": "`",
        "KC_CAPS": "Caps",
        "KC_LEFT": "←",
        "KC_RGHT": "→",
        "MO(_NAV_MEDIA)": "Nav/Media",
    }
    if keycode in labels:
        return labels[keycode]
    if keycode.startswith("KC_") and len(keycode) == 4:
        return keycode[-1]
    return keycode


def key_svg(key: Key, keycode: str) -> str:
    cx = key.x + KEY_W / 2
    label = html.escape(keycode_label(keycode))
    return f"""\
  <g class="key">
    <rect x="{key.x}" y="{key.y}" width="{KEY_W}" height="{KEY_H}" rx="12"/>
    <text class="key-label" x="{cx:g}" y="{key.y + 28}">{label}</text>
    <text class="key-meta" x="{cx:g}" y="{key.y + 51}">R{key.qmk_row}C{key.col}</text>
    <text class="key-pin" x="{cx:g}" y="{key.y + 70}">{ROW_PINS[key.qmk_row]} / {COL_PINS[key.col]}</text>
  </g>"""


def wiring_board_svg(key: Key) -> str:
    x = 115 + key.col * 146
    y = 785 + key.qmk_row * 112
    return f"""\
  <g class="pcb">
    <rect x="{x}" y="{y}" width="104" height="72" rx="18"/>
    <circle class="row-pad" cx="{x + 19}" cy="{y + 36}" r="8"/>
    <circle class="col-pad" cx="{x + 85}" cy="{y + 36}" r="8"/>
    <text class="pad-letter" x="{x + 19}" y="{y + 40}">R</text>
    <text class="pad-letter" x="{x + 85}" y="{y + 40}">C</text>
    <rect class="switch" x="{x + 39}" y="{y + 22}" width="26" height="28" rx="5"/>
    <path class="internal" d="M{x + 27} {y + 36} H{x + 39} M{x + 65} {y + 36} H{x + 77}"/>
    <rect class="band" x="{x + 72}" y="{y + 27}" width="5" height="18"/>
    <text class="pcb-index" x="{x + 52}" y="{y + 66}">R{key.qmk_row}C{key.col}</text>
  </g>"""


def wiring_bus_svg(keys: list[Key]) -> str:
    parts: list[str] = []
    for row, pin in enumerate(ROW_PINS):
        row_keys = [key for key in keys if key.qmk_row == row]
        points = [(115 + key.col * 146 + 19, 785 + row * 112 + 36) for key in row_keys]
        start_x = points[0][0] - 45
        end_x = points[-1][0]
        y = points[0][1]
        parts.append(f'<path class="row-wire" d="M{start_x} {y} H{end_x}"/>')
        parts.append(f'<text class="row-label" x="{start_x - 10}" y="{y + 5}">R{row} · {pin}</text>')

    for col, pin in enumerate(COL_PINS):
        col_keys = [key for key in keys if key.col == col]
        x = 115 + col * 146 + 85
        start_y = 785 + col_keys[0].qmk_row * 112 + 36
        end_y = 785 + col_keys[-1].qmk_row * 112 + 36
        parts.append(f'<path class="col-wire" d="M{x} {start_y - 42} V{end_y}"/>')
        parts.append(f'<text class="col-label" x="{x}" y="{start_y - 53}">C{col}</text>')
        parts.append(f'<text class="col-pin-label" x="{x}" y="{start_y - 34}">{pin}</text>')
    return "\n".join(parts)


def generate_svg(keys: list[Key], keycodes: dict[tuple[int, int], str]) -> str:
    key_markup = "\n".join(
        key_svg(key, keycodes[(key.qmk_row, key.col)]) for key in keys
    )
    bus_markup = wiring_bus_svg(keys)
    board_markup = "\n".join(wiring_board_svg(key) for key in keys)

    return f"""\
<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="1440" height="1680" viewBox="0 0 1440 1680"
     role="img" aria-labelledby="title description">
  <title id="title">左手 29 键 Plum Twist 与 Joy-Con 焊接接线图</title>
  <desc id="description">RP2040-Zero 单手 5 行 6 列 ROW2COL 矩阵，最后一行缺最右键；Plum Twist 板载二极管阴极朝列；Joy-Con X、Y 与按压接线。</desc>
  <style>
    text {{ font-family: Inter, "SF Pro Text", "PingFang SC", "Microsoft YaHei", sans-serif; fill: #e9eef7; }}
    .bg {{ fill: #151922; }}
    .panel {{ fill: #202735; stroke: #536075; stroke-width: 2; }}
    .title {{ font-size: 32px; font-weight: 800; }}
    .subtitle {{ fill: #b9c5d6; font-size: 15px; }}
    .section {{ font-size: 22px; font-weight: 800; }}
    .key rect {{ fill: #29394a; stroke: #77b9dc; stroke-width: 2; }}
    .key-label {{ font-size: 18px; font-weight: 800; text-anchor: middle; }}
    .key-meta {{ fill: #bcd8e8; font-size: 13px; font-weight: 700; text-anchor: middle; }}
    .key-pin {{ fill: #ffd47b; font-size: 11px; font-weight: 650; text-anchor: middle; }}
    .warning-box {{ fill: #3a3022; stroke: #f0b65a; stroke-width: 2; }}
    .warning {{ fill: #ffd47b; font-size: 15px; font-weight: 700; }}
    .note {{ fill: #c4cfdd; font-size: 14px; }}
    .pcb rect:first-child {{ fill: #34303e; stroke: #ad8fc7; stroke-width: 2; }}
    .row-pad {{ fill: #69bde8; stroke: #d8f2ff; stroke-width: 1.5; }}
    .col-pad {{ fill: #e7b555; stroke: #fff0bd; stroke-width: 1.5; }}
    .pad-letter {{ fill: #151922; font-size: 11px; font-weight: 900; text-anchor: middle; }}
    .switch {{ fill: #505a6a; stroke: #dfe7ef; stroke-width: 1.5; }}
    .internal {{ stroke: #dfe7ef; stroke-width: 3; }}
    .band {{ fill: #11151b; }}
    .pcb-index {{ fill: #b7c1cf; font-size: 9px; text-anchor: middle; }}
    .row-wire {{ fill: none; stroke: #69bde8; stroke-width: 7; stroke-linecap: round; }}
    .col-wire {{ fill: none; stroke: #e7b555; stroke-width: 6; stroke-linecap: round; }}
    .row-label {{ fill: #9bdcff; font-size: 13px; font-weight: 800; text-anchor: end; }}
    .col-label {{ fill: #ffd47b; font-size: 13px; font-weight: 800; text-anchor: middle; }}
    .col-pin-label {{ fill: #e6c984; font-size: 11px; font-weight: 700; text-anchor: middle; }}
    .controller {{ fill: #252d3b; stroke: #7a879b; stroke-width: 2; }}
    .controller-title {{ font-size: 19px; font-weight: 800; text-anchor: middle; }}
    .pin {{ font-size: 13px; font-weight: 700; }}
    .joy {{ fill: #34302e; stroke: #dc7e39; stroke-width: 3; }}
    .joy-stick {{ fill: #4b4642; stroke: #f1c25f; stroke-width: 3; }}
    .wire-vcc {{ stroke: #ef5350; }}
    .wire-gnd {{ stroke: #aeb6c2; }}
    .wire-x {{ stroke: #9dbb4b; }}
    .wire-y {{ stroke: #55a6ad; }}
    .wire-sw {{ stroke: #c185d8; }}
    .joy-wire {{ fill: none; stroke-width: 5; stroke-linecap: round; }}
    .flow {{ stroke: #e7edf5; stroke-width: 3; fill: none; marker-end: url(#arrow); }}
    .diode {{ fill: #d99749; stroke: #ffd18b; stroke-width: 2; }}
    .diode-band {{ fill: #11151b; }}
    .flow-label {{ font-size: 14px; font-weight: 800; text-anchor: middle; }}
  </style>
  <defs>
    <marker id="arrow" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto">
      <path d="M0,0 L0,6 L8,3 z" fill="#e7edf5"/>
    </marker>
  </defs>

  <rect class="bg" width="1440" height="1680"/>
  <rect class="panel" x="24" y="20" width="1392" height="1640" rx="24"/>
  <text class="title" x="58" y="62">左手 29 键 + Joy-Con · Plum Twist 焊接接线图</text>
  <text class="subtitle" x="58" y="88">单手 RP2040-Zero · 5×6 矩阵（R4C5 不安装）· 从热插拔座/焊盘侧观察 · RGB 焊盘留空</text>

  <text class="section" x="58" y="128">第一层键位与 GPIO</text>
{key_markup}
  <rect class="warning-box" x="978" y="142" width="390" height="475" rx="18"/>
  <text class="section" x="1008" y="180">Plum Twist 单键 PCB</text>
  <text class="note" x="1008" y="204">视角：热插拔座/焊盘侧（实际焊接面）</text>
  <rect class="controller" x="1042" y="235" width="260" height="170" rx="54"/>
  <circle class="row-pad" cx="1082" cy="320" r="17"/>
  <circle class="col-pad" cx="1262" cy="320" r="17"/>
  <text class="pad-letter" x="1082" y="325">R</text>
  <text class="pad-letter" x="1262" y="325">C</text>
  <rect class="switch" x="1131" y="296" width="46" height="48" rx="7"/>
  <rect class="diode" x="1193" y="306" width="42" height="28" rx="14"/>
  <rect class="diode-band" x="1225" y="306" width="7" height="28"/>
  <path class="flow" d="M1099 320 H1125 M1178 320 H1188 M1236 320 H1241"/>
  <text class="flow-label" x="1172" y="372">R → 开关 → 板载二极管 → C</text>
  <text class="warning" x="1008" y="438">QMK 必须设置：ROW2COL</text>
  <text class="warning" x="1008" y="466">二极管阴极/条纹端固定朝 Column</text>
  <text class="note" x="1008" y="498">不需要外接 1N4148。</text>
  <text class="note" x="1008" y="524">每块 PCB：R 焊盘接同行蓝线；</text>
  <text class="note" x="1008" y="547">C 焊盘接同列黄线。</text>
  <text class="note" x="1008" y="576">+ / − / I / O（RGB）全部留空。</text>

  <line x1="58" y1="650" x2="1382" y2="650" stroke="#536075" stroke-width="2"/>
  <text class="section" x="58" y="690">29 块 PCB 的行列总线</text>
  <text class="subtitle" x="58" y="716">蓝色连接所有 R 焊盘；黄色连接所有 C 焊盘。交叉处不焊接，必须绝缘。</text>
{bus_markup}
{board_markup}

  <rect class="controller" x="1010" y="750" width="355" height="540" rx="18"/>
  <text class="controller-title" x="1188" y="788">RP2040-Zero 引脚总表</text>
  <text class="pin" x="1042" y="830">R0 → GP14</text>
  <text class="pin" x="1042" y="858">R1 → GP15</text>
  <text class="pin" x="1042" y="886">R2 → GP26</text>
  <text class="pin" x="1042" y="914">R3 → GP27</text>
  <text class="pin" x="1042" y="942">R4 → GP9</text>
  <text class="pin" x="1190" y="830">C0 → GP2</text>
  <text class="pin" x="1190" y="858">C1 → GP3</text>
  <text class="pin" x="1190" y="886">C2 → GP4</text>
  <text class="pin" x="1190" y="914">C3 → GP5</text>
  <text class="pin" x="1190" y="942">C4 → GP6</text>
  <text class="pin" x="1190" y="970">C5 → GP7</text>
  <line x1="1038" y1="992" x2="1338" y2="992" stroke="#536075" stroke-width="2"/>
  <text class="pin" x="1042" y="1028">Joy X → GP28 / ADC2</text>
  <text class="pin" x="1042" y="1056">Joy Y → GP29 / ADC3</text>
  <text class="pin" x="1042" y="1084">Joy SW → GP8（内部上拉）</text>
  <text class="pin" x="1042" y="1112">Joy VCC → 3V3</text>
  <text class="pin" x="1042" y="1140">Joy GND → GND</text>
  <text class="warning" x="1042" y="1182">Joy-Con 绝对不要接 5V</text>
  <text class="note" x="1042" y="1214">无右手、无 TRS、无分体数据线。</text>
  <text class="note" x="1042" y="1240">GP0/GP1 保留；GP8 只给摇杆按压。</text>

  <line x1="58" y1="1332" x2="1382" y2="1332" stroke="#536075" stroke-width="2"/>
  <text class="section" x="58" y="1372">Joy-Con 5 针转接板</text>
  <rect class="joy" x="70" y="1410" width="260" height="185" rx="28"/>
  <circle class="joy-stick" cx="200" cy="1483" r="48"/>
  <text class="controller-title" x="200" y="1570">Joy-Con 摇杆</text>
  <text class="note" x="200" y="1590" text-anchor="middle">5P FPC 转接板</text>
  <rect class="controller" x="1040" y="1395" width="320" height="215" rx="18"/>
  <text class="controller-title" x="1200" y="1430">RP2040-Zero</text>
  <text class="pin" x="1080" y="1470">3V3</text>
  <text class="pin" x="1080" y="1500">GND</text>
  <text class="pin" x="1080" y="1530">GP28</text>
  <text class="pin" x="1080" y="1560">GP29</text>
  <text class="pin" x="1080" y="1590">GP8</text>
  <path class="joy-wire wire-vcc" d="M330 1440 C600 1390 820 1390 1040 1470"/>
  <path class="joy-wire wire-gnd" d="M330 1470 C600 1450 820 1450 1040 1500"/>
  <path class="joy-wire wire-x" d="M330 1500 C600 1500 820 1500 1040 1530"/>
  <path class="joy-wire wire-y" d="M330 1530 C600 1550 820 1550 1040 1560"/>
  <path class="joy-wire wire-sw" d="M330 1560 C600 1610 820 1610 1040 1590"/>
  <text class="pin" x="355" y="1422">VCC → 3V3</text>
  <text class="pin" x="505" y="1472">GND → GND</text>
  <text class="pin" x="640" y="1508">X → GP28</text>
  <text class="pin" x="775" y="1552">Y → GP29</text>
  <text class="pin" x="885" y="1600">SW → GP8</text>
  <text class="warning" x="390" y="1640">固件：X/Y → WASD；SW 按下（接地）→ Space。上电时松开摇杆并静置约 1 秒。</text>
</svg>
"""


def main() -> None:
    keys = main_keys()
    keycodes = base_keycodes()
    generated_coordinates = {(key.qmk_row, key.col) for key in keys}
    visible_coordinates = vial_visible_coordinates()

    if len(keys) != 29 or len(keys) != len(generated_coordinates):
        raise SystemExit("SVG layout must contain 29 unique keys")
    if generated_coordinates != visible_coordinates:
        missing = sorted(visible_coordinates - generated_coordinates)
        extra = sorted(generated_coordinates - visible_coordinates)
        raise SystemExit(f"SVG/Vial coordinate mismatch; missing={missing}, extra={extra}")

    OUTPUT.write_text(generate_svg(keys, keycodes), encoding="utf-8")
    print(f"generated {OUTPUT.relative_to(ROOT)} with {len(keys)} visible keys")


if __name__ == "__main__":
    main()
