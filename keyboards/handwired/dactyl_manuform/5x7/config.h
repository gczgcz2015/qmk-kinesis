// Copyright 2026 gczgcz2015
// SPDX-License-Identifier: GPL-2.0-or-later

#pragma once

// The right half is the USB master and hosts the PMW3360. The left half's
// matrix uses the split transport, so both halves still use the same UF2.
#define MASTER_RIGHT

// RP2040 PIO half-duplex split transport over the TRS data conductor.
#define SERIAL_USART_TX_PIN GP0

// Ogen Lite V1.3 / PMW3360 on the right half. GP9-GP13 are kept together in
// the controller's center region; GP13 is reserved for a future MOTION line.
#define SPLIT_POINTING_ENABLE
#define POINTING_DEVICE_RIGHT
#define SPI_DRIVER SPID1
#define SPI_SCK_PIN GP10
#define SPI_MOSI_PIN GP11
#define SPI_MISO_PIN GP12
#define PMW33XX_CS_PIN GP9
#define PMW33XX_CPI 1600U
#define POINTING_DEVICE_ROTATION_90
// Reverse both output axes relative to the previous mounted orientation.
#define POINTING_DEVICE_INVERT_X

// Mirror reactive RGB state between two independent 27-LED chains.
#define SPLIT_TRANSPORT_MIRROR

// Four Vial-editable keyboard layers.
#define DYNAMIC_KEYMAP_LAYER_COUNT 4

// Enter the UF2 bootloader by pressing RESET twice quickly.
#define RP2040_BOOTLOADER_DOUBLE_TAP_RESET
#define RP2040_BOOTLOADER_DOUBLE_TAP_RESET_TIMEOUT 500U
