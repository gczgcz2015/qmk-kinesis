# Kinesis-style Dactyl Manuform 5x7

这是一个精简的 QMK 固件仓库，直接修改 QMK 现有目标
`handwired/dactyl_manuform/5x7`，用于以下硬件：

- 两块 Waveshare RP2040-Zero
- 左侧固定为 USB 主控
- 每侧 6 行 × 7 列，共 84 个手焊开关
- 每个开关一颗 1N4148，方向为 `COL2ROW`
- 三芯 TRS 连接左右半边：数据、5V、GND
- QMK PIO `vendor` 半双工分体通信
- VIA 四层动态键位
- VIA 显示 76 个 Advantage360 风格键位，隐藏 8 个扩展矩阵位置
- 无外接 RGB、OLED 或旋钮

## 仓库内容

- `keyboards/handwired/dactyl_manuform/5x7/`：RP2040 键盘配置与 VIA keymap
- `via/kinesis-dactyl-5x7.json`：VIA Design 标签页加载的定义
- `docs/WIRING.md`：完整接线、二极管方向和刷写步骤
- `scripts/build.sh`：固定使用 QMK 0.33.0 的本地 Docker 构建
- `.github/workflows/build.yml`：push 自动编译，tag 自动发布

USB/VIA 标识：

- VID：`0x4743`
- PID：`0x0001`
- 设备名：`Kinesis Dactyl 5x7`

## 构建

本机需要 Git、Python 3 和正在运行的 Docker。

```sh
make validate
make build
```

首次构建会把 QMK `0.33.0` 克隆到 `.build/qmk_firmware`，然后将本仓库中的
5x7 修改覆盖到该工作树并使用 QMK 官方 Docker 构建流程编译。输出文件位于
`dist/`：

- `handwired_dactyl_manuform_5x7_via.uf2`

也可以使用现有的完整 QMK 0.33.0 工作树：

```sh
QMK_HOME=/path/to/qmk_firmware make build
```

`QMK_HOME` 必须是完整 Git 仓库并正好位于 tag `0.33.0`。用户提供的
`/Users/paul/Downloads/qmk_firmware` 是参考文件快照，不是完整 QMK 工作树，
不能直接编译。

## 刷写

1. 断开电脑 USB 和左右 TRS。
2. 单独把一侧 RP2040-Zero 接到电脑。
3. 按住 `BOOT` 并点按 `RESET`，或快速按两次 `RESET`，进入 `RPI-RP2` 磁盘。
4. 把同一个 UF2 文件复制到该磁盘。
5. 断开这一侧，对另一侧重复操作。
6. 两侧都断电时插入 TRS。
7. 只把左侧 USB-C 接到电脑。

左右使用相同固件；`MASTER_LEFT` 固定左侧为主控。

## VIA

1. 刷入 `via` 固件并连接左侧 USB。
2. 打开 VIA，启用 Design 标签页。
3. 加载 `via/kinesis-dactyl-5x7.json`。
4. 在 Configure 中编辑 Base、Keypad、Fn、Navigation/Media 四层。

VIA JSON 故意不显示以下八个矩阵位置：

`0,6`、`4,5`、`4,6`、`5,3`、`6,6`、`10,5`、`10,6`、`11,3`。

每侧主键区按 `6/7/7/7/5` 排列，中间三行的第七键组成靠中央的功能键竖列；
六键拇指区向内镜像旋转，其中 Backspace/Delete 与 Enter/Space 使用纵向 2u
显示，其余四键为 1u。2u 仅是 VIA 中的布局尺寸，每个键仍对应一个矩阵交点。

这些键在默认固件中为 `KC_NO`。如需使用，可将对应坐标重新加入 VIA JSON。

## 安全要求

- TRS 只能在两侧完全断电后插拔。
- TRS 已连接时，禁止同时给两侧 USB-C 供电。
- 右侧正常使用时由左侧通过 TRS 的 5V 供电。

详细接线见 [docs/WIRING.md](docs/WIRING.md)。
