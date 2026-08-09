// Copyright 2026 gczgcz2015
// SPDX-License-Identifier: GPL-2.0-or-later

#pragma once

#define VIAL_KEYBOARD_UID {0xB8, 0x69, 0x89, 0xDC, 0x93, 0xBD, 0x1F, 0x64}

// Physical Escape (R2/C0) + Right Arrow (R4/C4).
#define VIAL_UNLOCK_COMBO_ROWS { 2, 4 }
#define VIAL_UNLOCK_COMBO_COLS { 0, 4 }

// 29 Plum Twist SK6812 LEDs powered directly from the RP2040-Zero 3V3 pin.
// The low ceiling protects the board's 3.3 V regulator under solid white.
#define RGB_MATRIX_LED_COUNT 29
#define RGB_MATRIX_SLEEP

#define ENABLE_RGB_MATRIX_BREATHING
#define ENABLE_RGB_MATRIX_CYCLE_LEFT_RIGHT
#define ENABLE_RGB_MATRIX_CYCLE_UP_DOWN
#define ENABLE_RGB_MATRIX_RAINBOW_MOVING_CHEVRON
#define ENABLE_RGB_MATRIX_SOLID_REACTIVE_SIMPLE
#define ENABLE_RGB_MATRIX_SPLASH
