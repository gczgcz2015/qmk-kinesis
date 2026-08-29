# Kinesis-style Dactyl Manuform 5x7+5x9

这是一个精简的 Vial-QMK 固件仓库，覆盖上游目标
`handwired/dactyl_manuform/5x7`，用于一把左右不对称的手焊分体键盘：

- 两块 YD-RP2040，刷入同一个 UF2
- 右侧固定为 USB 主端
- 左侧：32 个主键 + 6 个拇指键
- 右侧：37 个主键 + 6 个拇指键
- 右侧主键九列从左到右为 `4 / 2 / 2 / 4 / 5 / 5 / 5 / 5 / 5`
- 每个开关一颗 1N4148，方向为 `COL2ROW`
- 三芯 TRS 连接左右半边：GP0 数据、右 `Vout` 到左 `Vin`、GND
- 右侧 Ogen Lite V1.3 / PMW3360 轨迹球
- Vial 中可分配 `CPI-`、`CPI+`，16 档灵敏度（每档 200 CPI）断电保存
- Vial 四层动态键位，VIA 布局文件同步维护
- 无外接 RGB、OLED、旋钮或滚动模式

USB 标识：

- VID：`0x4743`
- PID：`0x0002`
- 设备名：`Kinesis Dactyl 5x7+5x9`

## 仓库内容

- `keyboards/handwired/dactyl_manuform/5x7/`：QMK 硬件配置和 VIA/Vial keymap
- `keyboards/handwired/dactyl_manuform/5x7/keymaps/vial/vial.json`：Vial 81 键布局
- `via/kinesis-dactyl-5x7.json`：同步的旧 VIA 布局
- `docs/WIRING.md`：完整接线、矩阵、供电和调试步骤
- `docs/wiring-layout.svg`：逐键矩阵/GPIO 接线图
- `scripts/validate_layout.py`：布局、引脚、CPI 和文档源数据校验
- `scripts/build.sh`：固定 Vial-QMK 提交的 Docker 构建

## 构建

本机需要 Git、Python 3 和正在运行的 Docker。

```sh
make validate
make wiring-svg
make build
```

首次构建会把 `vial-kb/vial-qmk` 克隆到 `.build/vial-qmk`，检出固定提交
`00fc4627cd038ac9b7e9b8bf2b40b50e9e88aecb`，再覆盖本仓库配置并编译。
输出文件：

```text
dist/handwired_dactyl_manuform_5x7_vial.uf2
```

目标路径和 UF2 文件名为兼容上游而保留 `5x7`；USB 设备名和实际布局已经更新为
`5x7+5x9`。

## 刷写与连接

1. 拔掉电脑 USB，并断开 TRS。
2. 单独连接一侧 YD-RP2040。
3. 按住 `BOOT` 并点按 `RESET`，或快速按两次 `RESET`，进入 `RPI-RP2`。
4. 复制同一个 UF2 到该磁盘。
5. 另一侧重复以上步骤。
6. 两侧都断电时插好 TRS。
7. 只把右侧 USB-C 接到电脑。

固件使用 `MASTER_RIGHT`。左侧单独接 USB 时会临时被识别为右半，因此完整测试必须
连接 TRS，并从右侧 USB 上电。

## Vial 与 CPI

Vial 的 User 分类包含两个可分配键码：

- `CPI-`：降低一档
- `CPI+`：提高一档

档位为：

```text
200 → 400 → 600 → … → 3200 CPI（每档 200 CPI）
```

默认 `1600 CPI`。达到上下限后停止，不循环；当前档位写入 EEPROM，断电后保留。
执行 EEPROM Reset 后恢复默认值。Base 层的五个新增右键默认为：

```text
       C0          C1          C2
R0   Keypad       CPI-        CPI+
R1     Fn       Mouse Left  Mouse Right
R2  Nav/Media      ·           ·
R3 Mouse Middle    ·           ·
```

其他三层使用透明键，因此这些轨迹球控制在所有层都可用。

Vial 解锁组合保持为实体 `Escape + Enter`。

## 安全要求

- Ogen Lite 的 `VCC` 只能接 `3V3`，绝不能接 `Vin`、`Vout` 或 TRS 电源。
- TRS 只能在两侧完全断电时插拔。
- TRS 已连接时，只允许右侧连接 USB。
- TRS Ring 必须是右侧 `Vout → 左侧 Vin`，不能把两个引脚笼统当作同一个 5V 点。
- 行列交叉处必须绝缘；所有二极管带环端朝行线。

完整接线见 [docs/WIRING.md](docs/WIRING.md)。
