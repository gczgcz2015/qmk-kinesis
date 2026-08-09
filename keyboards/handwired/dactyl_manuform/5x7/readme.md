# Dactyl Manuform asymmetric 5x7+5x9 YD-RP2040 override

This repository overlays Vial-QMK's `handwired/dactyl_manuform/5x7`
target with an asymmetric 12x9 split matrix:

- YD-RP2040 controllers on both halves
- fixed right USB master
- 38 visible keys on the left and 43 on the right
- right-side Ogen Lite V1.3 / PMW3360
- persistent Vial-assignable CPI up/down keycodes
- four dynamic Vial layers

Build:

```sh
make handwired/dactyl_manuform/5x7:vial
```

The target path remains `5x7` for upstream compatibility; the USB product name
is `Kinesis Dactyl 5x7+5x9`. Read the repository-level
`docs/WIRING.md` before connecting power or TRS.
