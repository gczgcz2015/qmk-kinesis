// Copyright 2026 gczgcz2015
// SPDX-License-Identifier: GPL-2.0-or-later

#include QMK_KEYBOARD_H

enum layer_names {
    _BASE,
    _KEYPAD,
    _FN,
    _NAV_MEDIA,
};

const uint16_t PROGMEM keymaps[][MATRIX_ROWS][MATRIX_COLS] = {
    [_BASE] = LAYOUT_5x7(
        // Left key well: 7 / 7 / 7 / 6 / 5 visible keys.
        KC_EQL,  KC_1,    KC_2,    KC_3,    KC_4,    KC_5,    TG(_KEYPAD),
        KC_TAB,  KC_Q,    KC_W,    KC_E,    KC_R,    KC_T,    MO(_FN),
        KC_ESC,  KC_A,    KC_S,    KC_D,    KC_F,    KC_G,    MO(_NAV_MEDIA),
        KC_LSFT, KC_Z,    KC_X,    KC_C,    KC_V,    KC_B,    XXXXXXX,
        MO(_NAV_MEDIA), KC_GRV, KC_CAPS, KC_LEFT, KC_RGHT, XXXXXXX, XXXXXXX,

        // Left thumb cluster. Matrix position 5,0 is intentionally hidden.
        KC_LCTL,
        XXXXXXX, KC_END,
        KC_DEL,  KC_LALT,
        KC_BSPC, KC_HOME,

        // Right key well: mirrored, with a three-key inner function column.
        TG(_KEYPAD), KC_6, KC_7,    KC_8,    KC_9,    KC_0,    KC_MINS,
        MO(_FN), KC_Y,    KC_U,    KC_I,    KC_O,    KC_P,    KC_BSLS,
        MO(_NAV_MEDIA), KC_H, KC_J, KC_K,    KC_L,    KC_SCLN, KC_QUOT,
        XXXXXXX, KC_N,    KC_M,    KC_COMM, KC_DOT,  KC_SLSH, KC_RSFT,
        XXXXXXX, XXXXXXX, KC_UP,   KC_DOWN, KC_LBRC, KC_RBRC, MO(_NAV_MEDIA),

        // Right thumb cluster. Matrix position 11,0 is intentionally hidden.
        KC_RCTL,
        KC_ENT,  KC_PGDN,
        XXXXXXX, KC_RGUI,
        KC_PGUP, KC_SPC
    ),

    [_KEYPAD] = LAYOUT_5x7(
        _______, _______, _______, _______, _______, _______, _______,
        _______, _______, _______, _______, _______, _______, _______,
        _______, _______, _______, _______, _______, _______, _______,
        _______, _______, _______, _______, _______, _______, XXXXXXX,
        _______, _______, _______, _______, _______, XXXXXXX, XXXXXXX,

        _______,
        XXXXXXX, _______,
        _______, _______,
        _______, _______,

        _______, _______, _______, _______, _______, _______, _______,
        _______, KC_P7,   KC_P8,   KC_P9,   KC_PMNS, KC_PSLS, _______,
        _______, KC_P4,   KC_P5,   KC_P6,   KC_PPLS, KC_PAST, _______,
        XXXXXXX, KC_P1,   KC_P2,   KC_P3,   KC_PENT, KC_PDOT, _______,
        XXXXXXX, XXXXXXX, _______, _______, KC_P0,   _______, _______,

        _______,
        _______, _______,
        XXXXXXX, _______,
        _______, _______
    ),

    [_FN] = LAYOUT_5x7(
        KC_F1,   KC_F2,   KC_F3,   KC_F4,   KC_F5,   KC_F6,   _______,
        _______, _______, _______, _______, _______, _______, _______,
        _______, _______, _______, _______, _______, _______, _______,
        _______, _______, _______, _______, _______, _______, XXXXXXX,
        _______, _______, _______, _______, _______, XXXXXXX, XXXXXXX,

        _______,
        XXXXXXX, _______,
        _______, _______,
        _______, _______,

        _______, KC_F7,   KC_F8,   KC_F9,   KC_F10,  KC_F11,  KC_F12,
        _______, _______, _______, _______, _______, _______, _______,
        _______, _______, _______, _______, _______, _______, _______,
        XXXXXXX, _______, _______, _______, _______, _______, _______,
        XXXXXXX, XXXXXXX, KC_VOLU, KC_VOLD, KC_MUTE, _______, _______,

        _______,
        KC_MPRV, KC_MNXT,
        XXXXXXX, _______,
        _______, _______
    ),

    [_NAV_MEDIA] = LAYOUT_5x7(
        _______, _______, _______, _______, _______, _______, _______,
        _______, _______, KC_HOME, KC_UP,   KC_END,  KC_PGUP, _______,
        _______, _______, KC_LEFT, KC_DOWN, KC_RGHT, KC_PGDN, _______,
        _______, _______, _______, _______, _______, _______, XXXXXXX,
        _______, _______, _______, _______, _______, XXXXXXX, XXXXXXX,

        _______,
        XXXXXXX, _______,
        _______, _______,
        _______, _______,

        _______, _______, _______, _______, _______, _______, _______,
        _______, KC_MPRV, KC_MPLY, KC_MNXT, KC_VOLU, _______, _______,
        _______, KC_LEFT, KC_DOWN, KC_UP,   KC_RGHT, KC_VOLD, _______,
        XXXXXXX, _______, _______, _______, KC_MUTE, _______, _______,
        XXXXXXX, XXXXXXX, _______, _______, _______, _______, _______,

        _______,
        _______, _______,
        XXXXXXX, _______,
        _______, _______
    )
};
