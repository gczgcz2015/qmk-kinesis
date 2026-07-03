#!/bin/sh
set -eu

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
VIAL_REF=${VIAL_REF:-00fc4627cd038ac9b7e9b8bf2b40b50e9e88aecb}
VIAL_HOME=${VIAL_HOME:-"$ROOT_DIR/.build/vial-qmk"}
TARGET=handwired/dactyl_manuform/5x7:vial

python3 "$ROOT_DIR/scripts/validate_layout.py"

if [ ! -d "$VIAL_HOME/.git" ]; then
    mkdir -p "$(dirname "$VIAL_HOME")"
    git clone \
        --branch vial \
        --depth 1 \
        --recurse-submodules \
        --shallow-submodules \
        https://github.com/vial-kb/vial-qmk.git \
        "$VIAL_HOME"
fi

CURRENT_REF=$(git -C "$VIAL_HOME" rev-parse HEAD)
if [ "$CURRENT_REF" != "$VIAL_REF" ]; then
    git -C "$VIAL_HOME" fetch --depth 1 origin "$VIAL_REF"
    git -C "$VIAL_HOME" checkout --detach "$VIAL_REF"
    git -C "$VIAL_HOME" submodule sync --recursive
    git -C "$VIAL_HOME" submodule update --init --recursive --depth 1
fi

rsync -a "$ROOT_DIR/keyboards/" "$VIAL_HOME/keyboards/"

(
    cd "$VIAL_HOME"
    SKIP_FLASHING_SUPPORT=1 ./util/docker_build.sh "$TARGET"
)

mkdir -p "$ROOT_DIR/dist"
cp "$VIAL_HOME/handwired_dactyl_manuform_5x7_vial.uf2" "$ROOT_DIR/dist/"

echo "firmware written to $ROOT_DIR/dist"
