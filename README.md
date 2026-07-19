# Kinesis-style Dactyl Manuform 5x7

这是一个精简的 QMK 固件仓库，直接修改 QMK 现有目标
`handwired/dactyl_manuform/5x7`，用于以下硬件：

- 两块 Waveshare RP2040-Zero
- 左侧固定为 USB 主控
- 每侧主键区 5 行矩阵，共 64 个手焊开关
- 每个开关一颗 1N4148，方向为 `COL2ROW`
- 三芯 TRS 连接左右半边：数据、5V、GND
- 左侧拇指区改为 1 个 Ogen Lite V1.3 / PMW3360 轨迹球，用于移动光标
- QMK PIO `vendor` 半双工分体通信
- Vial 四层动态键位，支持 Vial Web 自动识别
- Vial 显示 64 个主键，隐藏 20 个未接矩阵位置
- 无外接 RGB、OLED 或旋钮

## 仓库内容

- `keyboards/handwired/dactyl_manuform/5x7/`：RP2040 键盘配置，以及 Vial/VIA keymap
- `keyboards/handwired/dactyl_manuform/5x7/keymaps/vial/vial.json`：嵌入固件的 Vial 布局
- `via/kinesis-dactyl-5x7.json`：保留用于旧 VIA 固件的布局定义
- `docs/WIRING.md`：完整接线、二极管方向和刷写步骤
- `scripts/build.sh`：固定 Vial-QMK 提交的本地 Docker 构建
- `.github/workflows/build.yml`：push 自动编译，tag 自动发布

USB 标识：

- VID：`0x4743`
- PID：`0x0001`
- 设备名：`Kinesis Dactyl 5x7`

## 构建

本机需要 Git、Python 3 和正在运行的 Docker。

```sh
make validate
make build
```

首次构建会把 `vial-kb/vial-qmk` 克隆到 `.build/vial-qmk`，检出固定提交
`00fc4627cd038ac9b7e9b8bf2b40b50e9e88aecb`，然后覆盖本仓库中的 5x7
配置并使用 Vial-QMK Docker 构建流程编译。输出文件位于 `dist/`：

- `handwired_dactyl_manuform_5x7_vial.uf2`

也可以使用已检出上述提交的完整 Vial-QMK 工作树：

```sh
VIAL_HOME=/path/to/vial-qmk make build
```

普通的 `qmk/qmk_firmware` 工作树不能编译 Vial 固件；必须使用
[`vial-kb/vial-qmk`](https://github.com/vial-kb/vial-qmk)。

## 刷写

1. 断开电脑 USB 和左右 TRS。
2. 单独把一侧 RP2040-Zero 接到电脑。
3. 按住 `BOOT` 并点按 `RESET`，或快速按两次 `RESET`，进入 `RPI-RP2` 磁盘。
4. 把同一个 UF2 文件复制到该磁盘。
5. 断开这一侧，对另一侧重复操作。
6. 两侧都断电时插入 TRS。
7. 只把左侧 USB-C 接到电脑。

左右使用相同固件；`MASTER_LEFT` 固定左侧为主控。

## Vial Web

1. 两侧刷入同一个 `vial` UF2，并只连接左侧 USB。
2. 使用最新版 Chrome、Edge 或 Chromium 打开
   [Vial Web](https://vial.rocks/app/)。
3. 选择 `Kinesis Dactyl 5x7`，固件内嵌的布局会自动加载。
4. 在 Keymap 中编辑 Base、Keypad、Fn、Navigation/Media 四层。
5. 需要解锁安全功能时，在 Vial 中发起 Unlock，然后按住实体
   `Escape + Right Shift`，直到进度完成。

QMK 的完整 6×7×2 矩阵定义保留 84 个坐标；当前实体键盘和 Vial/VIA 布局使用
其中 64 个主键。以下 20 个位置无需安装开关或接线，并在 Vial/VIA 中隐藏：

`3,6`、`4,5`、`4,6`、左侧整行 `5,0`–`5,6`、
`9,6`、`10,5`、`10,6`、右侧整行 `11,0`–`11,6`。

每侧主键区按 `7/7/7/6/5` 排列，上面三行的第七键组成靠中央的功能键竖列。
原拇指区矩阵 `R5` 在本分支停用，固件中为 `NO_PIN`。`R4` 保持接在 `GP9`。
左侧 Ogen Lite 使用 SPI0：`GP2/GP3/GP4/GP5`。这些引脚原本属于矩阵列
`C0–C3`，因此轨迹球测试分支把四列设为 `NO_PIN`；必须把对应列线从控制器断开，
相关按键会暂时失效。

轨迹球测试固件只提供光标 X/Y 移动，默认 `1600 CPI`；不配置鼠标按键或滚轮。

## 安全要求

- TRS 只能在两侧完全断电后插拔。
- TRS 已连接时，禁止同时给两侧 USB-C 供电。
- 右侧正常使用时由左侧通过 TRS 的 5V 供电。

详细接线见 [docs/WIRING.md](docs/WIRING.md)。
