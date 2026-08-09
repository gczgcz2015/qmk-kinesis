// Copyright 2026 gczgcz2015
// SPDX-License-Identifier: GPL-2.0-or-later

#include "quantum.h"

#ifdef RGB_MATRIX_ENABLE

// Physical SK6812 chain, viewed as the key matrix:
//
//    R0  0   1   2   3   4   5  ->
//    R1 11  10   9   8   7   6  <-
//    R2 12  13  14  15  16  17  ->
//    R3 23  22  21  20  19  18  <-
//    R4 24  25  26  27  28   -  ->
//
// GP1 feeds LED 0 (R0C0); each PCB O pad feeds the next PCB I pad.
led_config_t g_led_config = {
    {
        // Key matrix coordinate to LED index.
        {0, 1, 2, 3, 4, 5},
        {11, 10, 9, 8, 7, 6},
        {12, 13, 14, 15, 16, 17},
        {23, 22, 21, 20, 19, 18},
        {24, 25, 26, 27, 28, NO_LED},
    },
    {
        // LED index to physical position on QMK's 224 x 64 canvas.
        {0, 0}, {45, 0}, {90, 0}, {134, 0}, {179, 0}, {224, 0},
        {224, 16}, {179, 16}, {134, 16}, {90, 16}, {45, 16}, {0, 16},
        {0, 32}, {45, 32}, {90, 32}, {134, 32}, {179, 32}, {224, 32},
        {224, 48}, {179, 48}, {134, 48}, {90, 48}, {45, 48}, {0, 48},
        {0, 64}, {45, 64}, {90, 64}, {134, 64}, {179, 64},
    },
    {
        // Every LED is mounted below a key switch.
        LED_FLAG_KEYLIGHT, LED_FLAG_KEYLIGHT, LED_FLAG_KEYLIGHT,
        LED_FLAG_KEYLIGHT, LED_FLAG_KEYLIGHT, LED_FLAG_KEYLIGHT,
        LED_FLAG_KEYLIGHT, LED_FLAG_KEYLIGHT, LED_FLAG_KEYLIGHT,
        LED_FLAG_KEYLIGHT, LED_FLAG_KEYLIGHT, LED_FLAG_KEYLIGHT,
        LED_FLAG_KEYLIGHT, LED_FLAG_KEYLIGHT, LED_FLAG_KEYLIGHT,
        LED_FLAG_KEYLIGHT, LED_FLAG_KEYLIGHT, LED_FLAG_KEYLIGHT,
        LED_FLAG_KEYLIGHT, LED_FLAG_KEYLIGHT, LED_FLAG_KEYLIGHT,
        LED_FLAG_KEYLIGHT, LED_FLAG_KEYLIGHT, LED_FLAG_KEYLIGHT,
        LED_FLAG_KEYLIGHT, LED_FLAG_KEYLIGHT, LED_FLAG_KEYLIGHT,
        LED_FLAG_KEYLIGHT, LED_FLAG_KEYLIGHT,
    },
};

#endif
