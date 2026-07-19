// Copyright 2026 gczgcz2015
// SPDX-License-Identifier: GPL-2.0-or-later

#pragma once

#define VIAL_KEYBOARD_UID {0xB8, 0x69, 0x89, 0xDC, 0x93, 0xBD, 0x1F, 0x64}

// Physical Escape (left R2/C0) + Right Shift (right R3/C0).
#define VIAL_UNLOCK_COMBO_ROWS { 2, 9 }
#define VIAL_UNLOCK_COMBO_COLS { 0, 0 }

// Ogen Lite V1.3 / PMW3360 on the left (USB master) half.
#define SPLIT_POINTING_ENABLE
#define POINTING_DEVICE_LEFT
#define SPI_DRIVER SPID0
#define SPI_SCK_PIN GP2
#define SPI_MOSI_PIN GP3
#define SPI_MISO_PIN GP4
#define PMW33XX_CS_PIN GP5
#define PMW33XX_CPI 1600U
