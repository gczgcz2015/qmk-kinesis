// Copyright 2026 gczgcz2015
// SPDX-License-Identifier: GPL-2.0-or-later

#include "quantum.h"

#ifdef RGB_MATRIX_ENABLE

// Each half has its own 27-LED GP1 chain. The main 4x6 area is wired in a
// row-by-row serpentine, followed by the three thumb keys on local row R4.
led_config_t g_led_config = {
    {
        // Left global rows R0-R4.
        {0, 1, 2, 3, 4, 5},
        {11, 10, 9, 8, 7, 6},
        {12, 13, 14, 15, 16, 17},
        {23, 22, 21, 20, 19, 18},
        {NO_LED, NO_LED, NO_LED, 24, 25, 26},
        // Right global rows R5-R9.
        {27, 28, 29, 30, 31, 32},
        {38, 37, 36, 35, 34, 33},
        {39, 40, 41, 42, 43, 44},
        {50, 49, 48, 47, 46, 45},
        {51, 52, 53, NO_LED, NO_LED, NO_LED},
    },
    {
        // Left main area.
        {0, 0}, {18, 0}, {36, 0}, {54, 0}, {72, 0}, {90, 0},
        {90, 16}, {72, 16}, {54, 16}, {36, 16}, {18, 16}, {0, 16},
        {0, 32}, {18, 32}, {36, 32}, {54, 32}, {72, 32}, {90, 32},
        {90, 48}, {72, 48}, {54, 48}, {36, 48}, {18, 48}, {0, 48},
        {54, 64}, {72, 64}, {90, 64},
        // Right main area.
        {134, 0}, {152, 0}, {170, 0}, {188, 0}, {206, 0}, {224, 0},
        {224, 16}, {206, 16}, {188, 16}, {170, 16}, {152, 16}, {134, 16},
        {134, 32}, {152, 32}, {170, 32}, {188, 32}, {206, 32}, {224, 32},
        {224, 48}, {206, 48}, {188, 48}, {170, 48}, {152, 48}, {134, 48},
        {134, 64}, {152, 64}, {170, 64},
    },
    {
        LED_FLAG_KEYLIGHT, LED_FLAG_KEYLIGHT, LED_FLAG_KEYLIGHT,
        LED_FLAG_KEYLIGHT, LED_FLAG_KEYLIGHT, LED_FLAG_KEYLIGHT,
        LED_FLAG_KEYLIGHT, LED_FLAG_KEYLIGHT, LED_FLAG_KEYLIGHT,
        LED_FLAG_KEYLIGHT, LED_FLAG_KEYLIGHT, LED_FLAG_KEYLIGHT,
        LED_FLAG_KEYLIGHT, LED_FLAG_KEYLIGHT, LED_FLAG_KEYLIGHT,
        LED_FLAG_KEYLIGHT, LED_FLAG_KEYLIGHT, LED_FLAG_KEYLIGHT,
        LED_FLAG_KEYLIGHT, LED_FLAG_KEYLIGHT, LED_FLAG_KEYLIGHT,
        LED_FLAG_KEYLIGHT, LED_FLAG_KEYLIGHT, LED_FLAG_KEYLIGHT,
        LED_FLAG_KEYLIGHT, LED_FLAG_KEYLIGHT, LED_FLAG_KEYLIGHT,
        LED_FLAG_KEYLIGHT, LED_FLAG_KEYLIGHT, LED_FLAG_KEYLIGHT,
        LED_FLAG_KEYLIGHT, LED_FLAG_KEYLIGHT, LED_FLAG_KEYLIGHT,
        LED_FLAG_KEYLIGHT, LED_FLAG_KEYLIGHT, LED_FLAG_KEYLIGHT,
        LED_FLAG_KEYLIGHT, LED_FLAG_KEYLIGHT, LED_FLAG_KEYLIGHT,
        LED_FLAG_KEYLIGHT, LED_FLAG_KEYLIGHT, LED_FLAG_KEYLIGHT,
        LED_FLAG_KEYLIGHT, LED_FLAG_KEYLIGHT, LED_FLAG_KEYLIGHT,
        LED_FLAG_KEYLIGHT, LED_FLAG_KEYLIGHT, LED_FLAG_KEYLIGHT,
        LED_FLAG_KEYLIGHT, LED_FLAG_KEYLIGHT, LED_FLAG_KEYLIGHT,
        LED_FLAG_KEYLIGHT, LED_FLAG_KEYLIGHT, LED_FLAG_KEYLIGHT,
    },
};

#endif
