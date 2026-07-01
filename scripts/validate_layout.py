#!/usr/bin/env python3
"""Validate the QMK and VIA matrix definitions without third-party packages."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
KEYBOARD_JSON = ROOT / "keyboards/handwired/dactyl_manuform/5x7/keyboard.json"
VIA_JSON = ROOT / "via/kinesis-dactyl-5x7.json"
KEYMAP_C = ROOT / "keyboards/handwired/dactyl_manuform/5x7/keymaps/via/keymap.c"
MATRIX_COORDINATE = re.compile(r"^(\d+),(\d+)$")
EXPECTED_HIDDEN = {
    (0, 6),
    (4, 5),
    (4, 6),
    (5, 3),
    (6, 6),
    (10, 5),
    (10, 6),
    (11, 3),
}


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def via_coordinates(value: object) -> set[tuple[int, int]]:
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
        raise ValueError("VIA layout contains a duplicate matrix coordinate")

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


def main() -> None:
    keyboard = load_json(KEYBOARD_JSON)
    via = load_json(VIA_JSON)
    keymap_source = KEYMAP_C.read_text(encoding="utf-8")

    layout = keyboard["layouts"]["LAYOUT_5x7"]["layout"]
    qmk_coordinates = {tuple(key["matrix"]) for key in layout}
    shown_coordinates = via_coordinates(via["layouts"]["keymap"])
    keymap_layers = layout_arguments(keymap_source)

    assert len(layout) == 84, f"QMK layout must contain 84 keys, got {len(layout)}"
    assert len(qmk_coordinates) == 84, "QMK layout contains duplicate matrix coordinates"
    assert len(shown_coordinates) == 76, (
        f"VIA must display 76 keys, got {len(shown_coordinates)}"
    )
    assert shown_coordinates <= qmk_coordinates, "VIA references an unknown matrix coordinate"
    assert qmk_coordinates - shown_coordinates == EXPECTED_HIDDEN, (
        "VIA hidden-key set does not match the intended eight keys"
    )
    assert via["matrix"] == {"rows": 12, "cols": 7}
    assert via["vendorId"] == keyboard["usb"]["vid"]
    assert via["productId"] == keyboard["usb"]["pid"]
    assert len(keymap_layers) == 4, f"expected 4 keymap layers, got {len(keymap_layers)}"
    assert all(len(layer) == 84 for layer in keymap_layers), (
        "every LAYOUT_5x7 keymap layer must contain 84 keycodes"
    )

    base_layer = keymap_layers[0]
    matrix_order = [tuple(key["matrix"]) for key in layout]
    hidden_keycodes = {
        coordinate: base_layer[index]
        for index, coordinate in enumerate(matrix_order)
        if coordinate in EXPECTED_HIDDEN
    }
    assert set(hidden_keycodes.values()) == {"XXXXXXX"}, (
        "all eight VIA-hidden keys must be KC_NO on the base layer"
    )

    print("layout validation passed: 84 wired keys, 76 VIA-visible keys, 8 hidden")


if __name__ == "__main__":
    main()
