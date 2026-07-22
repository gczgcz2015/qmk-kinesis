# Dactyl left-hand 5x6 RP2040-Zero override

This repository keeps Vial-QMK's existing `handwired/dactyl_manuform/5x7`
target path, but implements a standalone left-hand 5x6 matrix with 29 keys,
a Plum Twist `ROW2COL` matrix, and an analog Joy-Con with a push switch.

Build:

```sh
make handwired/dactyl_manuform/5x7:vial
```

See the repository-level `docs/WIRING.md` before connecting power or TRS.
