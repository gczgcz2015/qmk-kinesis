# Dactyl split 4x6+3 RP2040-Zero override

This repository keeps Vial-QMK's existing `handwired/dactyl_manuform/5x7`
target path but implements a 54-key split `4x6+3` keyboard using two
RP2040-Zero controllers. The left half is the USB master; the right half has a
PMW3360 pointing device on SPI1. Both halves use GP1 VialRGB chains and the
same UF2.

Build:

```sh
make handwired/dactyl_manuform/5x7:vial
```

See the repository-level `docs/WIRING.md` before connecting power or TRS.
