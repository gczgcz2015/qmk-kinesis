// Copyright 2026 gczgcz2015
// SPDX-License-Identifier: GPL-2.0-or-later

#include QMK_KEYBOARD_H

enum layer_names {
    _BASE,
    _KEYPAD,
    _FN,
    _NAV_MEDIA,
};

enum custom_keycodes {
    PMW_CPI_DN = QK_KB_0,
    PMW_CPI_UP,
};

#define USER_CONFIG_MAGIC 0x54420400UL
#define USER_CONFIG_MASK  0xFFFFFF00UL
#define CPI_DEFAULT_INDEX 5

static const uint16_t cpi_levels[] = {
    100, 200, 400, 800, 1200, 1600, 2400, 3200,
};
static uint8_t cpi_index = CPI_DEFAULT_INDEX;

static void apply_cpi(bool persist) {
    pointing_device_set_cpi(cpi_levels[cpi_index]);
    if (persist) {
        eeconfig_update_user(USER_CONFIG_MAGIC | cpi_index);
    }
}

const uint16_t PROGMEM keymaps[][MATRIX_ROWS][MATRIX_COLS] = {
    [_BASE] = LAYOUT_split_4x6_3(
        // Left 4x6 main area.
        KC_EQL,  KC_1,    KC_2,    KC_3,    KC_4,    KC_5,
        KC_TAB,  KC_Q,    KC_W,    KC_E,    KC_R,    KC_T,
        KC_ESC,  KC_A,    KC_S,    KC_D,    KC_F,    KC_G,
        KC_LSFT, KC_Z,    KC_X,    KC_C,    KC_V,    KC_B,
        // Left thumb keys: R4C3-R4C5.
        KC_LCTL, MO(_FN), KC_BSPC,

        // Right 4x6 main area.
        KC_6,    KC_7,    KC_8,    KC_9,    KC_0,    KC_MINS,
        KC_Y,    KC_U,    KC_I,    KC_O,    KC_P,    KC_BSLS,
        KC_H,    KC_J,    KC_K,    KC_L,    KC_SCLN, KC_QUOT,
        KC_N,    KC_M,    KC_COMM, KC_DOT,  KC_SLSH, KC_RSFT,
        // Right thumb keys: R9C0-R9C2.
        KC_ENT, KC_SPC, MO(_NAV_MEDIA)
    ),

    [_KEYPAD] = LAYOUT_split_4x6_3(
        _______, _______, _______, _______, _______, _______,
        _______, _______, _______, _______, _______, _______,
        _______, _______, _______, _______, _______, _______,
        _______, _______, _______, _______, _______, _______,
        _______, _______, _______,

        _______, _______, _______, _______, _______, _______,
        KC_P7,   KC_P8,   KC_P9,   KC_PMNS, KC_PSLS, _______,
        KC_P4,   KC_P5,   KC_P6,   KC_PPLS, KC_PAST, _______,
        KC_P1,   KC_P2,   KC_P3,   KC_PENT, KC_PDOT, _______,
        _______, _______, _______
    ),

    [_FN] = LAYOUT_split_4x6_3(
        KC_F1,   KC_F2,   KC_F3,   KC_F4,   KC_F5,   KC_F6,
        _______, _______, _______, _______, _______, _______,
        _______, _______, _______, _______, _______, _______,
        _______, _______, _______, _______, _______, _______,
        _______, _______, _______,

        KC_F7,   KC_F8,   KC_F9,   KC_F10,  KC_F11,  KC_F12,
        _______, _______, _______, _______, _______, _______,
        _______, _______, _______, _______, _______, _______,
        _______, _______, _______, _______, _______, _______,
        PMW_CPI_DN, PMW_CPI_UP, _______
    ),

    [_NAV_MEDIA] = LAYOUT_split_4x6_3(
        _______, _______, _______, _______, _______, _______,
        _______, _______, KC_HOME, KC_UP,   KC_END,  KC_PGUP,
        _______, _______, KC_LEFT, KC_DOWN, KC_RGHT, KC_PGDN,
        _______, _______, _______, _______, _______, _______,
        _______, _______, _______,

        _______, _______, _______, _______, _______, _______,
        KC_MPRV, KC_MPLY, KC_MNXT, KC_VOLU, KC_VOLD, KC_MUTE,
        KC_LEFT, KC_DOWN, KC_UP,   KC_RGHT, _______, _______,
        KC_BTN3, _______, _______, _______, _______, _______,
        KC_BTN1, KC_BTN2, _______
    )
};

void eeconfig_init_user(void) {
    cpi_index = CPI_DEFAULT_INDEX;
    eeconfig_update_user(USER_CONFIG_MAGIC | cpi_index);
}

void keyboard_post_init_user(void) {
    if (!is_keyboard_master()) {
        return;
    }

    const uint32_t stored       = eeconfig_read_user();
    const uint8_t  stored_index = stored & 0xFFU;
    if ((stored & USER_CONFIG_MASK) == USER_CONFIG_MAGIC &&
        stored_index < (sizeof(cpi_levels) / sizeof(cpi_levels[0]))) {
        cpi_index = stored_index;
    } else {
        // Reset once when upgrading from the previous five-layer layout.
        dynamic_keymap_reset();
        cpi_index = CPI_DEFAULT_INDEX;
        eeconfig_update_user(USER_CONFIG_MAGIC | cpi_index);
    }
    apply_cpi(false);
    set_auto_mouse_enable(true);
}

bool process_record_user(uint16_t keycode, keyrecord_t *record) {
    switch (keycode) {
        case PMW_CPI_DN:
            if (record->event.pressed && cpi_index > 0) {
                cpi_index--;
                apply_cpi(true);
            }
            return false;
        case PMW_CPI_UP:
            if (record->event.pressed &&
                cpi_index + 1 < (sizeof(cpi_levels) / sizeof(cpi_levels[0]))) {
                cpi_index++;
                apply_cpi(true);
            }
            return false;
    }
    return true;
}
