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

#define CPI_CONFIG_MAGIC 0x43504D00UL
#define CPI_CONFIG_MASK  0xFFFFFF00UL
#define CPI_DEFAULT_INDEX 15

static const uint16_t cpi_levels[] = {
     100,  200,  300,  400,  500,  600,  700,  800,
     900, 1000, 1100, 1200, 1300, 1400, 1500, 1600,
    1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400,
    2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200,
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

// Speed-adaptive pointer acceleration. The thresholds are expressed at the
// reference CPI so changing the stored CPI does not change the feel of the
// acceleration curve.
#define TRACKBALL_ACCEL_REFERENCE_CPI 1600U
#define TRACKBALL_ACCEL_START        8U
#define TRACKBALL_ACCEL_MAX          32U
#define TRACKBALL_ACCEL_MAX_FACTOR   300U

static uint16_t trackball_accel_factor(uint16_t speed) {
    if (speed <= TRACKBALL_ACCEL_START) {
        return 100U;
    }
    if (speed >= TRACKBALL_ACCEL_MAX) {
        return TRACKBALL_ACCEL_MAX_FACTOR;
    }

    return 100U + (uint16_t)(((uint32_t)(speed - TRACKBALL_ACCEL_START) *
                              (TRACKBALL_ACCEL_MAX_FACTOR - 100U)) /
                             (TRACKBALL_ACCEL_MAX - TRACKBALL_ACCEL_START));
}

static int16_t trackball_scale_axis(int16_t value, uint16_t factor) {
    int32_t scaled = (int32_t)value * factor;
    scaled += scaled >= 0 ? 50 : -50;

    if (scaled > 12700) {
        return 127;
    }
    if (scaled < -12700) {
        return -127;
    }
    return (int16_t)(scaled / 100);
}

report_mouse_t pointing_device_task_user(report_mouse_t mouse_report) {
    int16_t x       = mouse_report.x;
    int16_t y       = mouse_report.y;
    uint16_t abs_x  = x < 0 ? (uint16_t)-x : (uint16_t)x;
    uint16_t abs_y  = y < 0 ? (uint16_t)-y : (uint16_t)y;
    uint16_t speed  = abs_x > abs_y ? abs_x : abs_y;
    uint16_t current_cpi = pointing_device_get_cpi();

    if (current_cpi == 0U) {
        current_cpi = TRACKBALL_ACCEL_REFERENCE_CPI;
    }

    const uint16_t normalized_speed = (uint16_t)(((uint32_t)speed *
                                                   TRACKBALL_ACCEL_REFERENCE_CPI +
                                                   current_cpi / 2U) /
                                                  current_cpi);
    const uint16_t factor = trackball_accel_factor(normalized_speed);

    mouse_report.x = (mouse_xy_report_t)trackball_scale_axis(x, factor);
    mouse_report.y = (mouse_xy_report_t)trackball_scale_axis(y, factor);
    return mouse_report;
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
