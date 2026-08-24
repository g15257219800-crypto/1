# GE22L × M48×2 ED 直通接头三维

派克目录没有 `GE22LM48X2ED` 现货。本模型按图纸包络尺寸建模，未注结构对齐派克 Ermeto **GE-M-ED**：

- 22L 锥端：`GE22LMED`（螺母螺纹 M30×2，通孔 D3=18，颈部 Ø27.5）
- M48×2 ED 螺柱：`GE42LMED`（六角 AF55，螺柱长 22，Form E 退刀槽）

螺纹按派克 Part Community 习惯做成**公称大径圆柱 + 倒角**（不建螺旋牙），便于装配干涉检查。

## 文件

| 文件 | 说明 |
|------|------|
| `GE22LM48X2ED.step` | STEP，可进 SolidWorks / NX / Inventor |
| `GE22LM48X2ED.stl` | 网格预览 |
| `GE22LM48X2ED_section.step` | 剖切实体 |
| `GE22LM48X2ED_preview.png` | 三维预览 |
| `GE22LM48X2ED_section.png` | 剖视预览 |
| `GE22LM48X2ED_section2d.png` | 标注剖视 |
| `ge22l_m48x2_ed.py` | CadQuery 生成脚本 |

坐标系：Z=0 为 M48 端面，Z=70 为 M30 端面。

## 尺寸

| 项目 | 数值 | 来源 |
|------|------|------|
| 总长 | 70 | 图纸 |
| M30×2 段（含 24° 内锥） | 32 | 图纸 |
| 六角厚度 | 16 | 70−32−22 |
| M48×2 螺柱段 | 22 | 图纸，同 GE42LMED |
| 六角对边 AF | 55 | GE42LMED S1 |
| 锥口 Ø | 22 | 图纸 |
| 24° 内锥深 | 10 | 图纸（ISO 8434-1 夹角 24°，半角 12°） |
| 内台阶深 | 15 | 图纸 |
| 通孔 Ø | 18 | GE22LMED D3 |
| M30 颈部 Ø | 27.5 | GE22L T1KG |
| ED 退刀槽 Ø | 44 | DIN 3869 / ED48×2 类 |
| ED 密封台 Ø | 52 | Form E 端面 |

## 重新生成

```bash
python3 -m pip install -r cad/requirements.txt
python3 cad/ge22l_m48x2_ed.py
```
