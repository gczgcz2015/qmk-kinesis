# 左手 29 键 Plum Twist + Joy-Con 接线说明

本配置是一把独立的左手 USB 键盘：29 个机械键、一个 Joy-Con 模拟摇杆，主控为
RP2040-Zero。不保留右手、TRS 或任何分体通信。

完整接线图见 [wiring-layout.svg](wiring-layout.svg)，贴片二极管的近实物方向图见
[plum-twist-diode-orientation.png](plum-twist-diode-orientation.png)。Plum Twist PCB 的
焊盘定义与二极管方向以[官方接线说明](https://ryanis.cool/cosmos/plum-twist/wiring)为准。

## 关键结论：使用 ROW2COL

Plum Twist 预留了贴片二极管焊盘，但二极管需要自行焊接。其方向固定为 `ROW2COL`，
固件已相应设置为：

```json
"diode_direction": "ROW2COL"
```

电气方向是：

```text
行 Rn → 开关 → 二极管 A（阳极）→ K（阴极）→ 列 Cn
                         ↑
                   阴极/条纹端朝列
```

以官方照片的焊接面摆放 PCB（`I + − O` 在上、`R C` 在下）时，D1 位于中央开关孔
右侧：**二极管有色条纹端 K 朝左、朝中央开关孔；无条纹端 A 朝右、朝 PCB 外缘**。
如果翻到 PCB 平整的另一面观察，左右会镜像。

不要把固件改回 `COL2ROW`。把标为 `R` 的焊盘接到行线，把标为 `C` 的焊盘接到
列线。RGB 的 `+ / - / I / O` 焊盘本次全部留空。

官方当前 v0.2 KiCad 源文件的 D1 是 `SOD-323 HandSoldering`，器件值为
`1N4148W-7-F`（LCSC C2128）。如果你拿到的 PCB 修订版或卖家明确要求 SOD-123，
条纹方向仍按上述规则，但焊接前请先确认更大的 SOD-123 封装确实能落在两个焊盘上。

## 材料

- RP2040-Zero × 1
- Plum Twist 单键 PCB × 29
- MX 兼容开关 × 29
- 贴片开关二极管 × 29（按你的 PCB 修订版选择 SOD-123；官方 v0.2 源文件为 SOD-323 / 1N4148W）
- Joy-Con 摇杆 × 1
- Joy-Con 5P FPC 转接板 × 1
- 26–30 AWG 单芯绝缘线：矩阵行列
- 24–28 AWG 多芯软线：控制器和 Joy-Con

## 矩阵与引脚

矩阵为 5 行 × 6 列，最后一行缺最右侧的 `R4C5`，共 29 键。

```text
       C0 C1 C2 C3 C4 C5
R0     ○  ○  ○  ○  ○  ○
R1     ○  ○  ○  ○  ○  ○
R2     ○  ○  ○  ○  ○  ○
R3     ○  ○  ○  ○  ○  ○
R4     ○  ○  ○  ○  ○  —
```

| 矩阵线 | RP2040-Zero | 矩阵线 | RP2040-Zero |
|---|---|---|---|
| R0 | GP14 | C0 | GP2 |
| R1 | GP15 | C1 | GP3 |
| R2 | GP26 | C2 | GP4 |
| R3 | GP27 | C3 | GP5 |
| R4 | GP9 | C4 | GP6 |
|  |  | C5 | GP7 |

每块 Plum Twist PCB 的 `R` 焊盘接到所属的水平行线，`C` 焊盘接到所属的垂直列线。
行列线在其他位置交叉时必须绝缘，不可短接。

## Joy-Con 接线

| Joy-Con 5P 转接板 | RP2040-Zero | 固件功能 |
|---|---|---|
| VCC | 3V3 | 3.3 V 供电 |
| GND | GND | 地 |
| X / VRX | GP28 / ADC2 | 左=A，右=D |
| Y / VRY | GP29 / ADC3 | 上=W，下=S |
| SW / BTN | GP8 | 按下=Space |

`SW` 按下时应把 GP8 短接到 GND；固件已启用内部上拉和 10 ms 去抖。

不要把 Joy-Con 的 VCC 接到 5V。RP2040 的 GPIO/ADC 只允许 3.3 V 逻辑。

上电时松开摇杆并静置约 1 秒。固件先等待 250 ms，再收集 32 个稳定样本校准中心；
校准期间摇杆按压仍然可以使用。方向轴带低通滤波及按下/释放滞回，并支持斜向同时
触发两个 WASD 键。

## 默认基础层

```text
=       1     2     3      4      5
Tab     Q     W     E      R      T
Esc     A     S     D      F      G
LShift  Z     X     C      V      B
Nav     `     Caps  Left   Right  [空]
```

Vial 解锁组合为 `Esc + Right Arrow`。

## 建议焊接顺序

1. 先把 29 块 Plum Twist PCB 装入外壳，确认朝向及热插拔座空间。
2. 按列连接六条 `C0..C5`，分别接到 GP2..GP7。
3. 按行连接五条 `R0..R4`，分别接到 GP14、GP15、GP26、GP27、GP9。
4. 用万用表确认任意两行、任意两列以及行列之间均没有意外短路。
5. 接 Joy-Con 的 3V3、GND、X、Y、SW；暂不焊 RGB。
6. 刷入固件后先逐键测试矩阵，再测试摇杆四向、斜向和按压。

## 上电前检查

1. 3V3、5V 与 GND 之间没有短路。
2. 每条行线之间、每条列线之间没有短路。
3. 未按键时行列不导通；按键后只在对应 R/C 交点通过贴片二极管单向导通。
4. 29 块 PCB 的 `R`、`C` 没有接反。
5. `R4C5` 未安装，GP8 没有误接成第七列。
6. Joy-Con VCC 接 3V3 而非 5V，SW 按下时连接 GP8 与 GND。
