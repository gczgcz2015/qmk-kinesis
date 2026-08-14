// Copyright 2026 gczgcz2015
// SPDX-License-Identifier: GPL-2.0-or-later

#pragma once

// The right half is always the USB master. Both halves use the same UF2.
#define MASTER_RIGHT

// RP2040 PIO half-duplex split transport over one TRS data conductor.
#define SERIAL_USART_TX_PIN GP0

// The left matrix is padded to nine logical columns with two unused pins.
// The right half uses all nine columns.
#define MATRIX_COL_PINS_RIGHT { GP2, GP3, GP4, GP5, GP6, GP7, GP8, GP9, GP10 }

// Ogen Lite V1.3 / PMW3360 on the right (USB master) half.
#define SPLIT_POINTING_ENABLE
#define POINTING_DEVICE_RIGHT
#define SPI_DRIVER SPID0
#define SPI_SCK_PIN GP18
#define SPI_MOSI_PIN GP19
#define SPI_MISO_PIN GP20
#define PMW33XX_CS_PIN GP21
#define PMW33XX_CPI 1600U
// The mounted sensor's +X axis points physically upward.
#define POINTING_DEVICE_ROTATION_90

// Four VIA/Vial-editable layers.
#define DYNAMIC_KEYMAP_LAYER_COUNT 4

// Enter the UF2 bootloader by pressing RESET twice quickly.
#define RP2040_BOOTLOADER_DOUBLE_TAP_RESET
#define RP2040_BOOTLOADER_DOUBLE_TAP_RESET_TIMEOUT 500U
