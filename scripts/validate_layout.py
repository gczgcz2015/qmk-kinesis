#!/usr/bin/env python3
"""Validate the split 4x6+3 PMW3360 QMK, VIA, Vial, and SVG data."""

from __future__ import annotations

import json
import re
from pathlib import Path

from generate_wiring_svg import main_keys


ROOT = Path(__file__).resolve().parents[1]
KEYBOARD_DIR = ROOT / "keyboards/handwired/dactyl_manuform/5x7"
KEYBOARD_JSON = KEYBOARD_DIR / "keyboard.json"
KEYBOARD_CONFIG = KEYBOARD_DIR / "config.h"
KEYBOARD_SOURCE = KEYBOARD_DIR / "5x7.c"
MCU_CONFIG = KEYBOARD_DIR / "mcuconf.h"
VIA_JSON = ROOT / "via/kinesis-dactyl-5x7.json"
VIAL_DIR = KEYBOARD_DIR / "keymaps/vial"
VIAL_JSON = VIAL_DIR / "vial.json"
VIAL_CONFIG = VIAL_DIR / "config.h"
VIA_CONFIG = KEYBOARD_DIR / "keymaps/via/config.h"
LAYOUT_NAME = "LAYOUT_split_4x6_3"
KEYMAPS = {
    "VIA": KEYBOARD_DIR / "keymaps/via/keymap.c",
    "Vial": VIAL_DIR / "keymap.c",
}
RULES = {
    "VIA": KEYBOARD_DIR / "keymaps/via/rules.mk",
    "Vial": VIAL_DIR / "rules.mk",
}
MATRIX_COORDINATE = re.compile(r"^(\d+),(\d+)$")
EXPECTED_COORDINATES = (
    {(row, col) for row in range(4) for col in range(6)}
    | {(4, col) for col in (3, 4, 5)}
    | {(row, col) for row in range(5, 9) for col in range(6)}
    | {(9, col) for col in (0, 1, 2)}
)
EXPECTED_UNLOCK_COORDINATES = {(2, 0), (9, 0)}
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


def macro_values(source: str, name: str) -> list[int]:
    match = re.search(rf"^#define\s+{name}\s+\{{([^}}]+)\}}", source, re.MULTILINE)
    if not match:
        raise ValueError(f"missing {name}")
    return [int(value.strip(), 0) for value in match.group(1).split(",")]


def require_define(source: str, name: str, value: str | None = None) -> None:
    suffix = "" if value is None else rf"\s+{re.escape(value)}"
    assert re.search(rf"^#define\s+{name}{suffix}\s*$", source, re.MULTILINE), (
        f"missing or incorrect #define {name}"
    )


def require_rule(source: str, name: str, value: str = "yes") -> None:
    assert re.search(rf"^{name}\s*=\s*{re.escape(value)}$", source, re.MULTILINE), (
        f"missing or incorrect rule {name}"
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
    svg_coordinates = {(key.qmk_row, key.col) for key in main_keys()}

    assert len(layout) == len(qmk_coordinates) == 54
    assert qmk_coordinates == EXPECTED_COORDINATES
    assert via_coordinates == vial_coordinates == EXPECTED_COORDINATES
    assert svg_coordinates == EXPECTED_COORDINATES
    assert vial["layouts"]["keymap"] == via["layouts"]["keymap"]

    expected_matrix = {"rows": 10, "cols": 6}
    assert via["matrix"] == vial["matrix"] == expected_matrix
    assert via["name"] == keyboard["keyboard_name"]
    assert via["vendorId"] == keyboard["usb"]["vid"] == "0x4743"
    assert via["productId"] == keyboard["usb"]["pid"] == "0x0003"
    assert keyboard["board"] == "GENERIC_RP_RP2040"
    assert keyboard["diode_direction"] == "ROW2COL"
    assert keyboard["split"]["enabled"] is True
    assert keyboard["split"]["serial"] == {"driver": "vendor"}
    assert keyboard["features"]["rgb_matrix"] is True
    assert keyboard["rgb_matrix"] == {
        "driver": "ws2812",
        "default": {"val": 16},
        "max_brightness": 32,
    }
    assert keyboard["ws2812"] == {"pin": "GP1", "driver": "vendor"}
    assert keyboard["matrix_pins"] == {
        "rows": ["GP14", "GP15", "GP26", "GP27", "GP8"],
        "cols": ["GP2", "GP3", "GP4", "GP5", "GP6", "GP7"],
    }

    config = KEYBOARD_CONFIG.read_text(encoding="utf-8")
    for name, value in {
        "MASTER_RIGHT": None,
        "SERIAL_USART_TX_PIN": "GP0",
        "SPLIT_POINTING_ENABLE": None,
        "POINTING_DEVICE_RIGHT": None,
        "SPI_DRIVER": "SPID1",
        "SPI_SCK_PIN": "GP10",
        "SPI_MOSI_PIN": "GP11",
        "SPI_MISO_PIN": "GP12",
        "PMW33XX_CS_PIN": "GP9",
        "PMW33XX_CPI": "1600U",
        "POINTING_DEVICE_ROTATION_90": None,
        "POINTING_DEVICE_INVERT_X": None,
        "POINTING_DEVICE_AUTO_MOUSE_ENABLE": None,
        "AUTO_MOUSE_DEFAULT_LAYER": "3",
        "AUTO_MOUSE_TIME": "1000",
        "SPLIT_TRANSPORT_MIRROR": None,
        "DYNAMIC_KEYMAP_LAYER_COUNT": "4",
    }.items():
        require_define(config, name, value)

    common_gpio = set(keyboard["matrix_pins"]["rows"] + keyboard["matrix_pins"]["cols"])
    common_gpio |= {"GP1", "GP0"}
    left_gpio = common_gpio
    right_gpio = common_gpio | {"GP9", "GP10", "GP11", "GP12"}
    edge_gpio = {f"GP{pin}" for pin in range(16)} | {f"GP{pin}" for pin in range(26, 30)}
    assert len(common_gpio) == 13
    assert len(left_gpio) == 13 and len(right_gpio) == 17
    assert left_gpio <= edge_gpio and right_gpio <= edge_gpio
    assert {"GP9", "GP10", "GP11", "GP12"} <= right_gpio
    assert "GP13" not in right_gpio

    mcu_config = MCU_CONFIG.read_text(encoding="utf-8")
    assert "RP_ADC_USE_ADC1" not in mcu_config
    require_define(mcu_config, "RP_SPI_USE_SPI1", "TRUE")

    parsed_keymaps: dict[str, list[list[str]]] = {}
    for name, path in KEYMAPS.items():
        source = path.read_text(encoding="utf-8")
        layers = layout_arguments(source)
        assert len(layers) == 4, f"{name}: expected 4 layers, got {len(layers)}"
        assert all(len(layer) == 54 for layer in layers), (
            f"{name}: every {LAYOUT_NAME} layer must contain 54 keycodes"
        )
        assert "100, 200, 400, 800, 1200, 1600, 2400, 3200" in source
        assert "PMW_CPI_DN = QK_KB_0" in source
        assert "pointing_device_set_cpi(" in source
        assert "set_auto_mouse_enable(true);" in source
        parsed_keymaps[name] = layers

    assert parsed_keymaps["Vial"] == parsed_keymaps["VIA"]
    fn_by_coordinate = dict(zip(matrix_order, parsed_keymaps["Vial"][2]))
    assert fn_by_coordinate[(9, 0)] == "PMW_CPI_DN"
    assert fn_by_coordinate[(9, 1)] == "PMW_CPI_UP"

    assert vial["lighting"] == "vialrgb"
    assert [item["shortName"] for item in vial["customKeycodes"]] == ["CPI-", "CPI+"]

    vial_config = VIAL_CONFIG.read_text(encoding="utf-8")
    via_config = VIA_CONFIG.read_text(encoding="utf-8")
    uid = macro_values(vial_config, "VIAL_KEYBOARD_UID")
    unlock_rows = macro_values(vial_config, "VIAL_UNLOCK_COMBO_ROWS")
    unlock_cols = macro_values(vial_config, "VIAL_UNLOCK_COMBO_COLS")
    assert len(uid) == 8 and all(0 <= value <= 0xFF for value in uid)
    assert set(zip(unlock_rows, unlock_cols)) == EXPECTED_UNLOCK_COORDINATES
    for source in (vial_config, via_config):
        require_define(source, "RGB_MATRIX_LED_COUNT", "54")
        assert macro_values(source, "RGB_MATRIX_SPLIT") == [27, 27]
        require_define(source, "RGB_MATRIX_SLEEP")

    for name, path in RULES.items():
        rules = path.read_text(encoding="utf-8")
        require_rule(rules, "VIA_ENABLE")
        require_rule(rules, "POINTING_DEVICE_ENABLE")
        require_rule(rules, "POINTING_DEVICE_DRIVER", "pmw3360")
        assert "ANALOG_DRIVER_REQUIRED" not in rules
        if name == "Vial":
            require_rule(rules, "VIAL_ENABLE")
            require_rule(rules, "VIALRGB_ENABLE")

    led_config = KEYBOARD_SOURCE.read_text(encoding="utf-8")
    compact_led_config = re.sub(r"\s+", "", led_config)
    for row in (
        "{0,1,2,3,4,5}",
        "{11,10,9,8,7,6}",
        "{12,13,14,15,16,17}",
        "{23,22,21,20,19,18}",
        "{NO_LED,NO_LED,NO_LED,24,25,26}",
        "{27,28,29,30,31,32}",
        "{38,37,36,35,34,33}",
        "{39,40,41,42,43,44}",
        "{50,49,48,47,46,45}",
        "{51,52,53,NO_LED,NO_LED,NO_LED}",
    ):
        assert row in compact_led_config
    assert led_config.count("LED_FLAG_KEYLIGHT") == 54

    vial_keymap = KEYMAPS["Vial"].read_text(encoding="utf-8")
    require_define(vial_keymap, "USER_CONFIG_MAGIC", "0x54420400UL")
    assert "if (!is_keyboard_master())" in vial_keymap
    assert "dynamic_keymap_reset();" in vial_keymap
    assert "JOYCON" not in vial_keymap.upper()
    assert "analogReadPin" not in vial_keymap
    assert "matrix_scan_user" not in vial_keymap

    print(
        "layout validation passed: split 10x6 matrix, 54 physical/VIA/Vial keys, "
        "right-master split, right-side GP9-GP12 PMW3360, 4 synchronized layers, "
        "eight CPI presets, and two 27-key GP1 RGB chains"
    )


if __name__ == "__main__":
    main()
