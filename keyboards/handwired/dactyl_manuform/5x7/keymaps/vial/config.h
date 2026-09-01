// Copyright 2026 gczgcz2015
// SPDX-License-Identifier: GPL-2.0-or-later

#pragma once

#define VIAL_KEYBOARD_UID {0x52, 0x50, 0x5A, 0x34, 0x36, 0x54, 0x42, 0x33}

// Physical Escape (left R2/C0) + Enter (right R9/C0).
#define VIAL_UNLOCK_COMBO_ROWS { 2, 9 }
#define VIAL_UNLOCK_COMBO_COLS { 0, 0 }

// Each RP2040-Zero powers one 27-key Plum Twist chain from 3V3.
#define RGB_MATRIX_LED_COUNT 54
#define RGB_MATRIX_SPLIT { 27, 27 }
#define RGB_MATRIX_SLEEP

#define ENABLE_RGB_MATRIX_BREATHING
#define ENABLE_RGB_MATRIX_CYCLE_LEFT_RIGHT
#define ENABLE_RGB_MATRIX_CYCLE_UP_DOWN
#define ENABLE_RGB_MATRIX_RAINBOW_MOVING_CHEVRON
#define ENABLE_RGB_MATRIX_SOLID_REACTIVE_SIMPLE
#define ENABLE_RGB_MATRIX_SPLASH
