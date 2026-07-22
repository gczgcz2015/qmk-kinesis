// Copyright 2026 gczgcz2015
// SPDX-License-Identifier: GPL-2.0-or-later

#include QMK_KEYBOARD_H
#include "analog.h"

enum layer_names {
    _BASE,
    _KEYPAD,
    _FN,
    _NAV_MEDIA,
};

const uint16_t PROGMEM keymaps[][MATRIX_ROWS][MATRIX_COLS] = {
    [_BASE] = LAYOUT_5x6(
        KC_EQL,  KC_1,    KC_2,    KC_3,    KC_4,    KC_5,
        KC_TAB,  KC_Q,    KC_W,    KC_E,    KC_R,    KC_T,
        KC_ESC,  KC_A,    KC_S,    KC_D,    KC_F,    KC_G,
        KC_LSFT, KC_Z,    KC_X,    KC_C,    KC_V,    KC_B,
        MO(_NAV_MEDIA), KC_GRV, KC_CAPS, KC_LEFT, KC_RGHT
    ),

    [_KEYPAD] = LAYOUT_5x6(
        _______, _______, _______, _______, _______, _______,
        _______, _______, _______, _______, _______, _______,
        _______, _______, _______, _______, _______, _______,
        _______, _______, _______, _______, _______, _______,
        _______, _______, _______, _______, _______
    ),

    [_FN] = LAYOUT_5x6(
        KC_F1,   KC_F2,   KC_F3,   KC_F4,   KC_F5,   KC_F6,
        _______, _______, _______, _______, _______, _______,
        _______, _______, _______, _______, _______, _______,
        _______, _______, _______, _______, _______, _______,
        _______, _______, _______, _______, _______
    ),

    [_NAV_MEDIA] = LAYOUT_5x6(
        _______, _______, _______, _______, _______, _______,
        _______, _______, KC_HOME, KC_UP,   KC_END,  KC_PGUP,
        _______, _______, KC_LEFT, KC_DOWN, KC_RGHT, KC_PGDN,
        _______, _______, _______, _______, _______, _______,
        _______, _______, _______, _______, _______
    )
};

enum joycon_input_index {
    JOYCON_LEFT,
    JOYCON_RIGHT,
    JOYCON_UP,
    JOYCON_DOWN,
    JOYCON_PRESS,
};

#define JOYCON_X_PIN GP28
#define JOYCON_Y_PIN GP29
#define JOYCON_SW_PIN GP8
#define JOYCON_ADC_DEFAULT_CENTER 512
#define JOYCON_PRESS_DELTA 110
#define JOYCON_RELEASE_DELTA 70
#define JOYCON_POLL_INTERVAL_MS 5
#define JOYCON_SW_DEBOUNCE_MS 10
#define JOYCON_CALIBRATION_DELAY_MS 250
#define JOYCON_CALIBRATION_SAMPLES 32
#define JOYCON_CALIBRATION_MAX_SPAN 24
#define JOYCON_CALIBRATION_CENTER_MIN 256
#define JOYCON_CALIBRATION_CENTER_MAX 768
#define JOYCON_FILTER_DIVISOR 2

static bool     joycon_pressed[5];
static uint16_t joycon_last_poll;
static bool     joycon_sw_raw_pressed;
static bool     joycon_sw_debounced_pressed;
static uint16_t joycon_sw_timer;
static bool     joycon_calibration_timer_started;
static uint16_t joycon_calibration_timer;
static bool     joycon_calibrated;
static uint8_t  joycon_calibration_count;
static int32_t  joycon_x_sum;
static int32_t  joycon_y_sum;
static int16_t  joycon_x_min;
static int16_t  joycon_x_max;
static int16_t  joycon_y_min;
static int16_t  joycon_y_max;
static int16_t  joycon_x_center = JOYCON_ADC_DEFAULT_CENTER;
static int16_t  joycon_y_center = JOYCON_ADC_DEFAULT_CENTER;
static int16_t  joycon_x_filtered = JOYCON_ADC_DEFAULT_CENTER;
static int16_t  joycon_y_filtered = JOYCON_ADC_DEFAULT_CENTER;

static void joycon_set_key(uint8_t index, uint16_t keycode, bool pressed) {
    if (pressed == joycon_pressed[index]) {
        return;
    }

    joycon_pressed[index] = pressed;
    if (pressed) {
        register_code16(keycode);
    } else {
        unregister_code16(keycode);
    }
}

static bool joycon_axis_negative(int16_t delta, bool currently_pressed) {
    const int16_t threshold = currently_pressed ? -JOYCON_RELEASE_DELTA : -JOYCON_PRESS_DELTA;
    return delta < threshold;
}

static bool joycon_axis_positive(int16_t delta, bool currently_pressed) {
    const int16_t threshold = currently_pressed ? JOYCON_RELEASE_DELTA : JOYCON_PRESS_DELTA;
    return delta > threshold;
}

static void joycon_release_directions(void) {
    joycon_set_key(JOYCON_LEFT, KC_A, false);
    joycon_set_key(JOYCON_RIGHT, KC_D, false);
    joycon_set_key(JOYCON_UP, KC_W, false);
    joycon_set_key(JOYCON_DOWN, KC_S, false);
}

static void joycon_update_button(void) {
    const bool pressed = !gpio_read_pin(JOYCON_SW_PIN);
    if (pressed != joycon_sw_raw_pressed) {
        joycon_sw_raw_pressed = pressed;
        joycon_sw_timer       = timer_read();
        return;
    }

    if (pressed != joycon_sw_debounced_pressed &&
        timer_elapsed(joycon_sw_timer) >= JOYCON_SW_DEBOUNCE_MS) {
        joycon_sw_debounced_pressed = pressed;
        joycon_set_key(JOYCON_PRESS, KC_SPC, pressed);
    }
}

static void joycon_reset_calibration_samples(void) {
    joycon_calibration_count = 0;
    joycon_x_sum             = 0;
    joycon_y_sum             = 0;
    joycon_x_min             = 1023;
    joycon_x_max             = 0;
    joycon_y_min             = 1023;
    joycon_y_max             = 0;
}

static void joycon_add_calibration_sample(int16_t x_raw, int16_t y_raw) {
    joycon_x_sum += x_raw;
    joycon_y_sum += y_raw;

    if (x_raw < joycon_x_min) {
        joycon_x_min = x_raw;
    }
    if (x_raw > joycon_x_max) {
        joycon_x_max = x_raw;
    }
    if (y_raw < joycon_y_min) {
        joycon_y_min = y_raw;
    }
    if (y_raw > joycon_y_max) {
        joycon_y_max = y_raw;
    }

    joycon_calibration_count++;
    if (joycon_calibration_count < JOYCON_CALIBRATION_SAMPLES) {
        return;
    }

    if (joycon_x_max - joycon_x_min > JOYCON_CALIBRATION_MAX_SPAN ||
        joycon_y_max - joycon_y_min > JOYCON_CALIBRATION_MAX_SPAN) {
        joycon_reset_calibration_samples();
        return;
    }

    const int16_t x_center = joycon_x_sum / JOYCON_CALIBRATION_SAMPLES;
    const int16_t y_center = joycon_y_sum / JOYCON_CALIBRATION_SAMPLES;
    if (x_center < JOYCON_CALIBRATION_CENTER_MIN || x_center > JOYCON_CALIBRATION_CENTER_MAX ||
        y_center < JOYCON_CALIBRATION_CENTER_MIN || y_center > JOYCON_CALIBRATION_CENTER_MAX) {
        joycon_reset_calibration_samples();
        return;
    }

    joycon_x_center   = x_center;
    joycon_y_center   = y_center;
    joycon_x_filtered = joycon_x_center;
    joycon_y_filtered = joycon_y_center;
    joycon_calibrated = true;
}

static int16_t joycon_filter_sample(int16_t filtered, int16_t raw) {
    return filtered + (raw - filtered) / JOYCON_FILTER_DIVISOR;
}

void keyboard_post_init_user(void) {
    gpio_set_pin_input_high(JOYCON_SW_PIN);
}

void matrix_scan_user(void) {
    if (!joycon_calibration_timer_started) {
        joycon_calibration_timer         = timer_read();
        joycon_calibration_timer_started = true;
        joycon_reset_calibration_samples();
    }

    if (timer_elapsed(joycon_last_poll) < JOYCON_POLL_INTERVAL_MS) {
        return;
    }
    joycon_last_poll = timer_read();
    joycon_update_button();

    if (timer_elapsed(joycon_calibration_timer) < JOYCON_CALIBRATION_DELAY_MS) {
        joycon_release_directions();
        return;
    }

    const int16_t x_raw = analogReadPin(JOYCON_X_PIN);
    const int16_t y_raw = analogReadPin(JOYCON_Y_PIN);

    if (!joycon_calibrated) {
        joycon_add_calibration_sample(x_raw, y_raw);
        joycon_release_directions();
        return;
    }

    joycon_x_filtered = joycon_filter_sample(joycon_x_filtered, x_raw);
    joycon_y_filtered = joycon_filter_sample(joycon_y_filtered, y_raw);

    const int16_t x_delta = joycon_x_filtered - joycon_x_center;
    const int16_t y_delta = joycon_y_filtered - joycon_y_center;

    joycon_set_key(
        JOYCON_LEFT,
        KC_A,
        joycon_axis_negative(x_delta, joycon_pressed[JOYCON_LEFT])
    );
    joycon_set_key(
        JOYCON_RIGHT,
        KC_D,
        joycon_axis_positive(x_delta, joycon_pressed[JOYCON_RIGHT])
    );
    joycon_set_key(
        JOYCON_UP,
        KC_W,
        joycon_axis_negative(y_delta, joycon_pressed[JOYCON_UP])
    );
    joycon_set_key(
        JOYCON_DOWN,
        KC_S,
        joycon_axis_positive(y_delta, joycon_pressed[JOYCON_DOWN])
    );
}
