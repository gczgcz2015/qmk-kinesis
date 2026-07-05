#!/usr/bin/env python3
"""Validate the QMK, VIA, and Vial matrix definitions without dependencies."""

from __future__ import annotations

import json
import re
from pathlib import Path

from generate_wiring_svg import main_keys, thumb_keys


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
EXPECTED_HIDDEN = {
    (3, 6),
    (4, 5),
    (4, 6),
    (5, 0),
    (9, 6),
    (10, 5),
    (10, 6),
    (11, 0),
}
EXPECTED_INNER_COLUMNS = {
    (0, 6),
    (1, 6),
    (2, 6),
    (6, 6),
    (7, 6),
    (8, 6),
}
EXPECTED_THUMB_COLUMNS_BY_POSITION = {
    ("L", 576, 630): 4,
    ("L", 672, 630): 6,
    ("L", 480, 720): 1,
    ("L", 576, 720): 2,
    ("L", 672, 720): 5,
    ("L", 672, 810): 3,
    ("R", 1050, 630): 6,
    ("R", 1146, 630): 4,
    ("R", 1050, 720): 5,
    ("R", 1146, 720): 2,
    ("R", 1242, 720): 1,
    ("R", 1050, 810): 3,
}
EXPECTED_THUMB_LAYOUT_ROWS = [
    ["5,4", "5,6"],
    ["5,1", "5,2", "5,5"],
    ["5,3"],
    ["11,6", "11,4"],
    ["11,5", "11,2", "11,1"],
    ["11,3"],
]
EXPECTED_BASE_THUMB_KEYCODES = {
    (5, 1): "KC_BSPC",
    (5, 2): "KC_DEL",
    (5, 3): "KC_END",
    (5, 4): "KC_LCTL",
    (5, 5): "KC_HOME",
    (5, 6): "KC_LALT",
    (11, 1): "KC_SPC",
    (11, 2): "KC_ENT",
    (11, 3): "KC_PGDN",
    (11, 4): "KC_RCTL",
    (11, 5): "KC_PGUP",
    (11, 6): "KC_RGUI",
}
EXPECTED_UNLOCK_COORDINATES = {(2, 0), (11, 2)}


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
    marker = "LAYOUT_5x7("
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

    layout = keyboard["layouts"]["LAYOUT_5x7"]["layout"]
    qmk_coordinates = {tuple(key["matrix"]) for key in layout}
    via_coordinates = visible_coordinates("VIA", via["layouts"]["keymap"])
    vial_coordinates = visible_coordinates("Vial", vial["layouts"]["keymap"])

    assert len(layout) == 84, f"QMK layout must contain 84 keys, got {len(layout)}"
    assert len(qmk_coordinates) == 84, "QMK layout contains duplicate matrix coordinates"
    assert len(via_coordinates) == 76, (
        f"VIA must display 76 keys, got {len(via_coordinates)}"
    )
    assert via_coordinates <= qmk_coordinates, "VIA references an unknown matrix coordinate"
    assert qmk_coordinates - via_coordinates == EXPECTED_HIDDEN, (
        "VIA hidden-key set does not match the intended eight keys"
    )
    assert vial_coordinates == via_coordinates, "Vial and VIA layouts must display the same keys"
    assert vial["layouts"]["keymap"] == via["layouts"]["keymap"], (
        "Vial and VIA visual geometry must stay in sync"
    )
    svg_keys = main_keys() + thumb_keys()
    svg_coordinates = {(key.qmk_row, key.col) for key in svg_keys}
    assert svg_coordinates == vial_coordinates, (
        "SVG and Vial/VIA must display the same matrix coordinates"
    )
    inner_column_coordinates = {
        (key.qmk_row, key.col) for key in svg_keys if key.col == 6 and key.local_row < 5
    }
    assert inner_column_coordinates == EXPECTED_INNER_COLUMNS, (
        "the visible three-key inner columns must use local rows R0/R1/R2"
    )
    row_y = {key.local_row: key.y for key in main_keys() if key.col == 0}
    assert all(
        key.y == row_y[key.local_row]
        for key in main_keys()
        if key.col == 6
    ), "every inner-column key must align with its electrical matrix row"
    thumb_columns_by_position = {
        (key.side, key.x, key.y): key.col for key in thumb_keys()
    }
    assert thumb_columns_by_position == EXPECTED_THUMB_COLUMNS_BY_POSITION, (
        "thumb matrix columns must match the documented physical wiring"
    )
    thumb_layout_rows = [
        [item for item in row if isinstance(item, str)]
        for row in vial["layouts"]["keymap"][8:]
    ]
    assert thumb_layout_rows == EXPECTED_THUMB_LAYOUT_ROWS, (
        "Vial thumb coordinates must match the optimized physical wiring"
    )
    assert via["matrix"] == {"rows": 12, "cols": 7}
    assert vial["matrix"] == {"rows": 12, "cols": 7}
    assert vial["lighting"] == "none"
    assert via["vendorId"] == keyboard["usb"]["vid"]
    assert via["productId"] == keyboard["usb"]["pid"]
    matrix_order = [tuple(key["matrix"]) for key in layout]

    parsed_keymaps: dict[str, list[list[str]]] = {}
    for name, path in KEYMAPS.items():
        keymap_layers = layout_arguments(path.read_text(encoding="utf-8"))
        assert len(keymap_layers) == 4, (
            f"{name}: expected 4 keymap layers, got {len(keymap_layers)}"
        )
        assert all(len(layer) == 84 for layer in keymap_layers), (
            f"{name}: every LAYOUT_5x7 keymap layer must contain 84 keycodes"
        )

        for layer_index, layer in enumerate(keymap_layers):
            hidden_keycodes = {
                coordinate: layer[index]
                for index, coordinate in enumerate(matrix_order)
                if coordinate in EXPECTED_HIDDEN
            }
            assert set(hidden_keycodes.values()) == {"XXXXXXX"}, (
                f"{name}: all eight hidden keys must be KC_NO on layer {layer_index}"
            )
        base_keycodes_by_coordinate = dict(zip(matrix_order, keymap_layers[0], strict=True))
        assert {
            coordinate: base_keycodes_by_coordinate[coordinate]
            for coordinate in EXPECTED_BASE_THUMB_KEYCODES
        } == EXPECTED_BASE_THUMB_KEYCODES, (
            f"{name}: base thumb functions must stay at their physical key positions"
        )
        parsed_keymaps[name] = keymap_layers

    assert parsed_keymaps["Vial"] == parsed_keymaps["VIA"], (
        "Vial and VIA default keymaps must stay in sync"
    )

    vial_config = VIAL_CONFIG.read_text(encoding="utf-8")
    uid = macro_values(vial_config, "VIAL_KEYBOARD_UID")
    unlock_rows = macro_values(vial_config, "VIAL_UNLOCK_COMBO_ROWS")
    unlock_cols = macro_values(vial_config, "VIAL_UNLOCK_COMBO_COLS")
    unlock_coordinates = set(zip(unlock_rows, unlock_cols, strict=True))
    assert len(uid) == 8 and all(0 <= value <= 0xFF for value in uid), (
        "VIAL_KEYBOARD_UID must contain eight bytes"
    )
    assert len(unlock_coordinates) >= 2, "Vial unlock combo must use at least two keys"
    assert unlock_coordinates <= vial_coordinates, (
        "Vial unlock combo must reference visible physical keys"
    )
    assert unlock_coordinates == EXPECTED_UNLOCK_COORDINATES, (
        "Vial unlock combo must stay on the physical Escape and Enter keys"
    )

    vial_rules = VIAL_RULES.read_text(encoding="utf-8")
    assert re.search(r"^VIA_ENABLE\s*=\s*yes$", vial_rules, re.MULTILINE)
    assert re.search(r"^VIAL_ENABLE\s*=\s*yes$", vial_rules, re.MULTILINE)

    print(
        "layout validation passed: 84 QMK matrix positions, "
        "76 wired/VIA/Vial-visible keys, 8 unused and hidden, "
        "4 synchronized layers"
    )


if __name__ == "__main__":
    main()
