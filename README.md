# Kinesis Dactyl Split 4×6 + 3

这是一个基于 Vial-QMK 的双 RP2040-Zero 分体键盘固件：

- 每侧 4×6 主键区 + 3 个拇指键，共 54 键
- Plum Twist `ROW2COL` 矩阵，每侧 27 颗 SK6812 逐键 RGB
- 左手固定为 USB 主控，不连接指针外设
- 右手 Ogen Lite V1.3 / PMW3360 轨迹球
- GP0 单线 PIO 分体通信，GP8 作为两侧拇指区矩阵行
- GP9–GP12 用于 PMW3360 SPI1，右手 GP13 预留
- Vial 四层动态键位
- 8 档持久 CPI：100、200、400、800、1200、1600、2400、3200

完整键位和接线图见 [docs/wiring-layout.svg](docs/wiring-layout.svg)，逐步说明见
[docs/WIRING.md](docs/WIRING.md)。

## 构建

本机需要 Git、Python 3 和正在运行的 Docker：

```sh
make validate
make build
```

构建固定使用 Vial-QMK 提交 `00fc4627cd038ac9b7e9b8bf2b40b50e9e88aecb`。输出固件：

```text
dist/handwired_dactyl_manuform_5x7_vial.uf2
```

也可以设置已有工作树：

```sh
VIAL_HOME=/path/to/vial-qmk make build
```

## 刷写

左右使用同一个 UF2：

1. 断开电脑 USB 和 TRS。
2. 单独连接一侧，按住 BOOT 并点按 RESET，或快速按两次 RESET。
3. 把 UF2 复制到 `RPI-RP2`。
4. 断开后对另一侧重复操作。
5. 两侧断电时连接 TRS，只给左手接 USB。

旧的单手固件不能与本固件混用，两侧都需要重新刷写。第一次升级会因
矩阵、PID 和 Vial UID 变化而恢复默认键位。

## Vial

USB 标识：

- VID：`0x4743`
- PID：`0x0003`
- 名称：`Kinesis Dactyl Split 4x6 Trackball`

Vial Layer 0–3 是四个普通键盘层。解锁组合为左手 Esc + 右手 Enter。

## 安全

- TRS 只能在两侧完全断电后插拔。
- TRS 已连接时禁止两侧同时接 USB。
- PMW3360 和 RGB 逻辑都使用 3.3 V。
- PMW3360 需要匹配透镜，并应撕掉透明运输保护膜。
