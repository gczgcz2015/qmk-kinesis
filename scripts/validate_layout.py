#!/usr/bin/env python3
"""Validate the standalone 29-key QMK, VIA, and Vial definitions."""

from __future__ import annotations

import json
import re
from pathlib import Path

from generate_wiring_svg import main_keys


ROOT = Path(__file__).resolve().parents[1]
KEYBOARD_JSON = ROOT / "keyboards/handwired/dactyl_manuform/5x7/keyboard.json"
VIA_JSON = ROOT / "via/kinesis-dactyl-5x7.json"
VIAL_DIR = ROOT / "keyboards/handwired/dactyl_manuform/5x7/keymaps/vial"
VIAL_JSON = VIAL_DIR / "vial.json"
VIAL_CONFIG = VIAL_DIR / "config.h"
VIAL_RULES = VIAL_DIR / "rules.mk"
KEYMAPS = {
    "VIA": ROOT / "keyboards/handwired/dactyl_manuform/5x7/keymaps/via/keymap.c",
    "Vial": VIAL_DIR / "keymap.c",
}
MATRIX_COORDINATE = re.compile(r"^(\d+),(\d+)$")
EXPECTED_COORDINATES = {
    (row, col)
    for row in range(5)
    for col in range(6)
    if (row, col) != (4, 5)
}
EXPECTED_UNLOCK_COORDINATES = {(2, 0), (4, 4)}


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def visible_coordinates(name: str, value: object) -> set[tuple[int, int]]:
    coordinates: list[tuple[int, int]] = []

    def collect(item: object) -> None:
        if isinstance(item, list):
            for child in item:
                collect(child)
        elif isinstance(item, str):
            match = MATRIX_COORDINATE.fullmatch(item)
            if match:
                coordinates.append((int(match.group(1)), int(match.group(2))))

    collect(value)
    unique_coordinates = set(coordinates)
    if len(unique_coordinates) != len(coordinates):
        raise ValueError(f"{name} layout contains a duplicate matrix coordinate")
    return unique_coordinates


def layout_arguments(source: str) -> list[list[str]]:
    source = re.sub(r"//.*", "", source)
    marker = "LAYOUT_5x6("
    layouts: list[list[str]] = []
    search_from = 0

    while (start := source.find(marker, search_from)) != -1:
        arguments: list[str] = []
        argument_start = start + len(marker)
        depth = 1
        index = argument_start

        while depth:
            character = source[index]
            if character == "(":
                depth += 1
            elif character == ")":
                depth -= 1
                if depth == 0:
                    arguments.append(source[argument_start:index].strip())
                    break
            elif character == "," and depth == 1:
                arguments.append(source[argument_start:index].strip())
                argument_start = index + 1
            index += 1

        layouts.append(arguments)
        search_from = index + 1

    return layouts


def macro_values(source: str, name: str) -> list[int]:
    match = re.search(rf"^#define\s+{name}\s+\{{([^}}]+)\}}", source, re.MULTILINE)
    if not match:
        raise ValueError(f"missing {name}")
    return [int(value.strip(), 0) for value in match.group(1).split(",")]


def main() -> None:
    keyboard = load_json(KEYBOARD_JSON)
    via = load_json(VIA_JSON)
    vial = load_json(VIAL_JSON)

    layout = keyboard["layouts"]["LAYOUT_5x6"]["layout"]
    qmk_coordinates = {tuple(key["matrix"]) for key in layout}
    via_coordinates = visible_coordinates("VIA", via["layouts"]["keymap"])
    vial_coordinates = visible_coordinates("Vial", vial["layouts"]["keymap"])

    assert len(layout) == 29, f"QMK layout must contain 29 keys, got {len(layout)}"
    assert qmk_coordinates == EXPECTED_COORDINATES
    assert via_coordinates == EXPECTED_COORDINATES
    assert vial_coordinates == EXPECTED_COORDINATES
    assert vial["layouts"]["keymap"] == via["layouts"]["keymap"], (
        "Vial and VIA visual geometry must stay in sync"
    )

    svg_coordinates = {(key.qmk_row, key.col) for key in main_keys()}
    assert svg_coordinates == EXPECTED_COORDINATES, (
        "SVG must contain the same 29 physical matrix positions"
    )

    expected_matrix = {"rows": 5, "cols": 6}
    assert via["matrix"] == expected_matrix
    assert vial["matrix"] == expected_matrix
    assert vial["lighting"] == "none"
    assert via["vendorId"] == keyboard["usb"]["vid"]
    assert via["productId"] == keyboard["usb"]["pid"]
    assert keyboard["diode_direction"] == "ROW2COL"
    assert "split" not in keyboard
    assert keyboard["matrix_pins"] == {
        "rows": ["GP14", "GP15", "GP26", "GP27", "GP9"],
        "cols": ["GP2", "GP3", "GP4", "GP5", "GP6", "GP7"],
    }

    parsed_keymaps: dict[str, list[list[str]]] = {}
    for name, path in KEYMAPS.items():
        keymap_layers = layout_arguments(path.read_text(encoding="utf-8"))
        assert len(keymap_layers) == 4, (
            f"{name}: expected 4 keymap layers, got {len(keymap_layers)}"
        )
        assert all(len(layer) == 29 for layer in keymap_layers), (
            f"{name}: every LAYOUT_5x6 layer must contain 29 keycodes"
        )
        parsed_keymaps[name] = keymap_layers

    assert parsed_keymaps["Vial"] == parsed_keymaps["VIA"], (
        "Vial and VIA default keymaps must stay in sync"
    )

    vial_config = VIAL_CONFIG.read_text(encoding="utf-8")
    uid = macro_values(vial_config, "VIAL_KEYBOARD_UID")
    unlock_rows = macro_values(vial_config, "VIAL_UNLOCK_COMBO_ROWS")
    unlock_cols = macro_values(vial_config, "VIAL_UNLOCK_COMBO_COLS")
    assert len(unlock_rows) == len(unlock_cols)
    unlock_coordinates = set(zip(unlock_rows, unlock_cols))
    assert len(uid) == 8 and all(0 <= value <= 0xFF for value in uid)
    assert unlock_coordinates == EXPECTED_UNLOCK_COORDINATES

    vial_rules = VIAL_RULES.read_text(encoding="utf-8")
    assert re.search(r"^VIA_ENABLE\s*=\s*yes$", vial_rules, re.MULTILINE)
    assert re.search(r"^VIAL_ENABLE\s*=\s*yes$", vial_rules, re.MULTILINE)
    assert re.search(r"^ANALOG_DRIVER_REQUIRED\s*=\s*yes$", vial_rules, re.MULTILINE)

    vial_keymap = KEYMAPS["Vial"].read_text(encoding="utf-8")
    assert re.search(r"^#define\s+JOYCON_X_PIN\s+GP28$", vial_keymap, re.MULTILINE)
    assert re.search(r"^#define\s+JOYCON_Y_PIN\s+GP29$", vial_keymap, re.MULTILINE)
    assert re.search(r"^#define\s+JOYCON_SW_PIN\s+GP8$", vial_keymap, re.MULTILINE)
    assert "gpio_set_pin_input_high(JOYCON_SW_PIN)" in vial_keymap
    assert "joycon_set_key(JOYCON_PRESS, KC_SPC, pressed)" in vial_keymap

    print(
        "layout validation passed: standalone 5x6 ROW2COL matrix, "
        "29 physical/VIA/Vial keys, 4 synchronized layers, Joy-Con X/Y/SW"
    )


if __name__ == "__main__":
    main()
