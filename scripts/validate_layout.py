#!/usr/bin/env python3
"""Validate the asymmetric QMK, VIA, Vial, trackball, and wiring definitions."""

from __future__ import annotations

import json
import re
from pathlib import Path

from generate_wiring_svg import main_keys, thumb_keys


ROOT = Path(__file__).resolve().parents[1]
KEYBOARD_DIR = ROOT / "keyboards/handwired/dactyl_manuform/5x7"
KEYBOARD_JSON = KEYBOARD_DIR / "keyboard.json"
KEYBOARD_CONFIG = KEYBOARD_DIR / "config.h"
VIA_JSON = ROOT / "via/kinesis-dactyl-5x7.json"
VIAL_DIR = KEYBOARD_DIR / "keymaps/vial"
VIAL_JSON = VIAL_DIR / "vial.json"
VIAL_CONFIG = VIAL_DIR / "config.h"
LAYOUT_NAME = "LAYOUT_5x7_5x9"
KEYMAPS = {
    "VIA": KEYBOARD_DIR / "keymaps/via/keymap.c",
    "Vial": VIAL_DIR / "keymap.c",
}
RULES = {
    "VIA": KEYBOARD_DIR / "keymaps/via/rules.mk",
    "Vial": VIAL_DIR / "rules.mk",
}
MATRIX_COORDINATE = re.compile(r"^(\d+),(\d+)$")
EXPECTED_UNLOCK_COORDINATES = {(2, 0), (11, 2)}
EXPECTED_RIGHT_COLUMN_COUNTS = {0: 4, 1: 2, 2: 2, 3: 4, 4: 5, 5: 5, 6: 5, 7: 5, 8: 5}
TRACKBALL_KEYS = {
    (6, 1): "PMW_CPI_DN",
    (6, 2): "PMW_CPI_UP",
    (7, 1): "KC_BTN1",
    (7, 2): "KC_BTN2",
    (9, 0): "KC_BTN3",
}


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
            if match := MATRIX_COORDINATE.fullmatch(item):
                coordinates.append((int(match.group(1)), int(match.group(2))))

    collect(value)
    unique = set(coordinates)
    if len(unique) != len(coordinates):
        raise ValueError(f"{name} layout contains duplicate matrix coordinates")
    return unique


def layout_arguments(source: str) -> list[list[str]]:
    source = re.sub(r"//.*", "", source)
    marker = f"{LAYOUT_NAME}("
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


def macro_tokens(source: str, name: str) -> list[str]:
    match = re.search(rf"^#define\s+{name}\s+\{{([^}}]+)\}}", source, re.MULTILINE)
    if not match:
        raise ValueError(f"missing {name}")
    return [value.strip() for value in match.group(1).split(",")]


def macro_ints(source: str, name: str) -> list[int]:
    return [int(value, 0) for value in macro_tokens(source, name)]


def require_define(source: str, name: str, value: str | None = None) -> None:
    suffix = "" if value is None else rf"\s+{re.escape(value)}"
    assert re.search(rf"^#define\s+{name}{suffix}\s*$", source, re.MULTILINE), (
        f"missing or incorrect #define {name}"
    )


def main() -> None:
    keyboard = load_json(KEYBOARD_JSON)
    via = load_json(VIA_JSON)
    vial = load_json(VIAL_JSON)

    layout = keyboard["layouts"][LAYOUT_NAME]["layout"]
    matrix_order = [tuple(key["matrix"]) for key in layout]
    qmk_coordinates = set(matrix_order)
    via_coordinates = visible_coordinates("VIA", via["layouts"]["keymap"])
    vial_coordinates = visible_coordinates("Vial", vial["layouts"]["keymap"])
    generated_keys = main_keys() + thumb_keys()
    generated_coordinates = {(key.qmk_row, key.col) for key in generated_keys}

    assert len(layout) == len(qmk_coordinates) == 81
    assert qmk_coordinates == via_coordinates == vial_coordinates == generated_coordinates
    assert vial["layouts"]["keymap"] == via["layouts"]["keymap"]
    assert vial["matrix"] == via["matrix"] == {"rows": 12, "cols": 9}
    assert vial["lighting"] == "none"
    assert [item["shortName"] for item in vial["customKeycodes"]] == ["CPI-", "CPI+"]
    assert via["name"] == keyboard["keyboard_name"] == "Kinesis Dactyl 5x7+5x9"
    assert via["vendorId"] == keyboard["usb"]["vid"] == "0x4743"
    assert via["productId"] == keyboard["usb"]["pid"] == "0x0002"

    left_keys = [key for key in generated_keys if key.side == "L"]
    right_keys = [key for key in generated_keys if key.side == "R"]
    assert len(left_keys) == 38 and len(right_keys) == 43
    right_main = [key for key in right_keys if key.local_row < 5]
    right_column_counts = {
        col: sum(key.col == col for key in right_main) for col in range(9)
    }
    assert right_column_counts == EXPECTED_RIGHT_COLUMN_COUNTS
    assert all(
        key.local_row in (0, 1)
        for key in right_main
        if key.col in (1, 2)
    ), "right C1/C2 must begin at R0 and occupy R0/R1"

    assert keyboard["matrix_pins"]["cols"] == [
        "GP2", "GP3", "GP4", "GP5", "GP6", "GP7", "GP8", "NO_PIN", "NO_PIN"
    ]
    assert keyboard["matrix_pins"]["rows"] == [
        "GP14", "GP15", "GP26", "GP27", "GP28", "GP29"
    ]

    config = KEYBOARD_CONFIG.read_text(encoding="utf-8")
    require_define(config, "MASTER_RIGHT")
    require_define(config, "SERIAL_USART_TX_PIN", "GP0")
    assert macro_tokens(config, "MATRIX_COL_PINS_RIGHT") == [
        "GP2", "GP3", "GP4", "GP5", "GP6", "GP7", "GP8", "GP9", "GP10"
    ]
    require_define(config, "SPLIT_POINTING_ENABLE")
    require_define(config, "POINTING_DEVICE_RIGHT")
    require_define(config, "POINTING_DEVICE_ROTATION_90")
    require_define(config, "POINTING_DEVICE_INVERT_Y")
    for macro, value in {
        "SPI_DRIVER": "SPID0",
        "SPI_SCK_PIN": "GP18",
        "SPI_MOSI_PIN": "GP19",
        "SPI_MISO_PIN": "GP20",
        "PMW33XX_CS_PIN": "GP21",
        "PMW33XX_CPI": "1600U",
    }.items():
        require_define(config, macro, value)

    parsed_keymaps: dict[str, list[list[str]]] = {}
    for name, path in KEYMAPS.items():
        source = path.read_text(encoding="utf-8")
        layers = layout_arguments(source)
        assert len(layers) == 4, f"{name}: expected four layers, got {len(layers)}"
        assert all(len(layer) == 81 for layer in layers), (
            f"{name}: every {LAYOUT_NAME} layer must contain 81 keycodes"
        )
        base_by_coordinate = dict(zip(matrix_order, layers[0]))
        for coordinate, keycode in TRACKBALL_KEYS.items():
            assert base_by_coordinate[coordinate] == keycode, (
                f"{name}: {coordinate} must default to {keycode}"
            )
        for layer in layers[1:]:
            by_coordinate = dict(zip(matrix_order, layer))
            assert all(by_coordinate[coordinate] == "_______" for coordinate in TRACKBALL_KEYS)

        assert "100,  200,  300,  400,  500,  600,  700,  800" in source
        assert "2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200" in source
        assert "#define CPI_CONFIG_MAGIC 0x43504D00UL" in source
        assert "#define CPI_DEFAULT_INDEX 15" in source
        assert "PMW_CPI_DN = QK_KB_0" in source
        assert "eeconfig_read_user()" in source and "eeconfig_update_user(" in source
        assert "pointing_device_set_cpi(" in source
        parsed_keymaps[name] = layers

    assert parsed_keymaps["Vial"] == parsed_keymaps["VIA"]

    vial_config = VIAL_CONFIG.read_text(encoding="utf-8")
    uid = macro_ints(vial_config, "VIAL_KEYBOARD_UID")
    unlock_rows = macro_ints(vial_config, "VIAL_UNLOCK_COMBO_ROWS")
    unlock_cols = macro_ints(vial_config, "VIAL_UNLOCK_COMBO_COLS")
    unlock_coordinates = set(zip(unlock_rows, unlock_cols))
    assert len(uid) == 8 and all(0 <= value <= 0xFF for value in uid)
    assert unlock_coordinates == EXPECTED_UNLOCK_COORDINATES
    assert unlock_coordinates <= vial_coordinates

    for name, path in RULES.items():
        rules = path.read_text(encoding="utf-8")
        assert re.search(r"^VIA_ENABLE\s*=\s*yes$", rules, re.MULTILINE)
        assert re.search(r"^POINTING_DEVICE_ENABLE\s*=\s*yes$", rules, re.MULTILINE)
        assert re.search(r"^POINTING_DEVICE_DRIVER\s*=\s*pmw3360$", rules, re.MULTILINE)
        if name == "Vial":
            assert re.search(r"^VIAL_ENABLE\s*=\s*yes$", rules, re.MULTILINE)

    print(
        "layout validation passed: 12x9 split matrix, 81 visible keys "
        "(38 left + 43 right), rotated right-master PMW3360, synchronized VIA/Vial layers, "
        "and persistent 32-step CPI controls"
    )


if __name__ == "__main__":
    main()
