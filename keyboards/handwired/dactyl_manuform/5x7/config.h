// Copyright 2026 gczgcz2015
// SPDX-License-Identifier: GPL-2.0-or-later

#pragma once

// The left half is always the USB master.
#define MASTER_LEFT

// RP2040 PIO half-duplex split transport over one TRS data conductor.
#define SERIAL_USART_TX_PIN GP0

// Four VIA/Vial-editable layers.
#define DYNAMIC_KEYMAP_LAYER_COUNT 4

// Enter the UF2 bootloader by pressing RESET twice quickly.
#define RP2040_BOOTLOADER_DOUBLE_TAP_RESET
#define RP2040_BOOTLOADER_DOUBLE_TAP_RESET_TIMEOUT 500U
