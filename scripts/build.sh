#!/bin/sh
set -eu

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
QMK_REF=${QMK_REF:-0.33.0}
QMK_HOME=${QMK_HOME:-"$ROOT_DIR/.build/qmk_firmware"}
TARGET=handwired/dactyl_manuform/5x7:via

python3 "$ROOT_DIR/scripts/validate_layout.py"

if [ ! -d "$QMK_HOME/.git" ]; then
    mkdir -p "$(dirname "$QMK_HOME")"
    git clone \
        --branch "$QMK_REF" \
        --depth 1 \
        --recurse-submodules \
        --shallow-submodules \
        https://github.com/qmk/qmk_firmware.git \
        "$QMK_HOME"
fi

if ! git -C "$QMK_HOME" describe --tags --exact-match 2>/dev/null | grep -qx "$QMK_REF"; then
    echo "error: $QMK_HOME is not checked out at QMK $QMK_REF" >&2
    exit 1
fi

rsync -a "$ROOT_DIR/keyboards/" "$QMK_HOME/keyboards/"

(
    cd "$QMK_HOME"
    SKIP_FLASHING_SUPPORT=1 ./util/docker_build.sh "$TARGET"
)

mkdir -p "$ROOT_DIR/dist"
cp "$QMK_HOME/handwired_dactyl_manuform_5x7_via.uf2" "$ROOT_DIR/dist/"
cp "$QMK_HOME/handwired_dactyl_manuform_5x7_via.bin" "$ROOT_DIR/dist/"

echo "firmware written to $ROOT_DIR/dist"

