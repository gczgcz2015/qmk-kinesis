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

#define CPI_CONFIG_MAGIC 0x43504A00UL
#define CPI_CONFIG_MASK  0xFFFFFF00UL
#define CPI_DEFAULT_INDEX 7

static const uint16_t cpi_levels[] = {
    200,  400,  600,  800,  1000, 1200, 1400, 1600,
    1800, 2000, 2200, 2400, 2600, 2800, 3000, 3200,
};
static uint8_t cpi_index = CPI_DEFAULT_INDEX;

static void apply_cpi(bool persist) {
    pointing_device_set_cpi(cpi_levels[cpi_index]);
    if (persist) {
        eeconfig_update_user(CPI_CONFIG_MAGIC | cpi_index);
    }
}

void eeconfig_init_user(void) {
    cpi_index = CPI_DEFAULT_INDEX;
    eeconfig_update_user(CPI_CONFIG_MAGIC | cpi_index);
}

void keyboard_post_init_user(void) {
    uint32_t stored = eeconfig_read_user();
    uint8_t stored_index = stored & 0xFFU;

    if ((stored & CPI_CONFIG_MASK) == CPI_CONFIG_MAGIC &&
        stored_index < (sizeof(cpi_levels) / sizeof(cpi_levels[0]))) {
        cpi_index = stored_index;
    } else {
        cpi_index = CPI_DEFAULT_INDEX;
        eeconfig_update_user(CPI_CONFIG_MAGIC | cpi_index);
    }
    apply_cpi(false);
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

const uint16_t PROGMEM keymaps[][MATRIX_ROWS][MATRIX_COLS] = {
    [_BASE] = LAYOUT_5x7_5x9(
        // Left key well: unchanged from main (7 / 7 / 7 / 6 / 5).
        KC_EQL,  KC_1,    KC_2,    KC_3,    KC_4,    KC_5,    TG(_KEYPAD),
        KC_TAB,  KC_Q,    KC_W,    KC_E,    KC_R,    KC_T,    MO(_FN),
        KC_ESC,  KC_A,    KC_S,    KC_D,    KC_F,    KC_G,    MO(_NAV_MEDIA),
        KC_LSFT, KC_Z,    KC_X,    KC_C,    KC_V,    KC_B,
        MO(_NAV_MEDIA), KC_GRV, KC_CAPS, KC_LEFT, KC_RGHT,

        // Left thumb cluster: C4, C6, C1, C2, C5, C3.
        KC_LCTL, KC_LALT,
        KC_BSPC, KC_DEL, KC_HOME,
        KC_END,

        // Right key well: columns contain 4 / 2 / 2 / 4 / 5 / 5 / 5 / 5 / 5 keys.
        TG(_KEYPAD), PMW_CPI_DN, PMW_CPI_UP, KC_6, KC_7, KC_8, KC_9, KC_0, KC_MINS,
        MO(_FN), KC_BTN1, KC_BTN2, KC_Y, KC_U, KC_I, KC_O, KC_P, KC_BSLS,
        MO(_NAV_MEDIA), KC_H, KC_J, KC_K, KC_L, KC_SCLN, KC_QUOT,
        KC_BTN3, KC_N, KC_M, KC_COMM, KC_DOT, KC_SLSH, KC_RSFT,
        KC_UP, KC_DOWN, KC_LBRC, KC_RBRC, MO(_NAV_MEDIA),

        // Right thumb cluster: C6, C4, C5, C2, C1, C3.
        KC_RGUI, KC_RCTL,
        KC_PGUP, KC_ENT, KC_SPC,
        KC_PGDN
    ),

    [_KEYPAD] = LAYOUT_5x7_5x9(
        _______, _______, _______, _______, _______, _______, _______,
        _______, _______, _______, _______, _______, _______, _______,
        _______, _______, _______, _______, _______, _______, _______,
        _______, _______, _______, _______, _______, _______,
        _______, _______, _______, _______, _______,

        _______, _______,
        _______, _______, _______,
        _______,

        _______, _______, _______, _______, _______, _______, _______, _______, _______,
        _______, _______, _______, KC_P7, KC_P8, KC_P9, KC_PMNS, KC_PSLS, _______,
        _______, KC_P4, KC_P5, KC_P6, KC_PPLS, KC_PAST, _______,
        _______, KC_P1, KC_P2, KC_P3, KC_PENT, KC_PDOT, _______,
        _______, _______, KC_P0, _______, _______,

        _______, _______,
        _______, _______, _______,
        _______
    ),

    [_FN] = LAYOUT_5x7_5x9(
        KC_F1, KC_F2, KC_F3, KC_F4, KC_F5, KC_F6, _______,
        _______, _______, _______, _______, _______, _______, _______,
        _______, _______, _______, _______, _______, _______, _______,
        _______, _______, _______, _______, _______, _______,
        _______, _______, _______, _______, _______,

        _______, _______,
        _______, _______, _______,
        _______,

        _______, _______, _______, KC_F7, KC_F8, KC_F9, KC_F10, KC_F11, KC_F12,
        _______, _______, _______, _______, _______, _______, _______, _______, _______,
        _______, _______, _______, _______, _______, _______, _______,
        _______, _______, _______, _______, _______, _______, _______,
        KC_VOLU, KC_VOLD, KC_MUTE, _______, _______,

        _______, _______,
        _______, KC_MPRV, _______,
        KC_MNXT
    ),

    [_NAV_MEDIA] = LAYOUT_5x7_5x9(
        _______, _______, _______, _______, _______, _______, _______,
        _______, _______, KC_HOME, KC_UP, KC_END, KC_PGUP, _______,
        _______, _______, KC_LEFT, KC_DOWN, KC_RGHT, KC_PGDN, _______,
        _______, _______, _______, _______, _______, _______,
        _______, _______, _______, _______, _______,

        _______, _______,
        _______, _______, _______,
        _______,

        _______, _______, _______, _______, _______, _______, _______, _______, _______,
        _______, _______, _______, KC_MPRV, KC_MPLY, KC_MNXT, KC_VOLU, _______, _______,
        _______, KC_LEFT, KC_DOWN, KC_UP, KC_RGHT, KC_VOLD, _______,
        _______, _______, _______, _______, KC_MUTE, _______, _______,
        _______, _______, _______, _______, _______,

        _______, _______,
        _______, _______, _______,
        _______
    )
};
