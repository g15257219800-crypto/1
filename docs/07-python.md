# 07 Python 脚本入门

FreeCAD 把 GUI 和几何内核绑在 Python 上。适合：批量改尺寸、参数扫描、从实验数据生成几何、写宏重复操作。

打开 **视图 → 面板 → Python 控制台**。仓库里有一份可直接执行的示例：[`examples/plate_with_hole.py`](../examples/plate_with_hole.py)。在 FreeCAD 中用 **宏 → 宏 → 执行** 打开该文件即可。

## 最小例子：带孔的板

在控制台逐段粘贴，或一次运行：

```python
import FreeCAD as App
import Part

doc = App.newDocument("DemoPlate")

# 80 x 50 x 8 的板，减去一个直径 8 的通孔
plate = Part.makeBox(80, 50, 8)
hole = Part.makeCylinder(4, 10, App.Vector(16, 25, -1))
solid = plate.cut(hole)

Part.show(solid, "Plate")
doc.recompute()
```

这是 **零件工作台风格** 的布尔：没有草图历史，改参数要改脚本再跑一遍。研究里扫孔径、板厚时，把 `80, 50, 8, 4` 提成变量，循环生成即可。

## 在已有文档里改属性

GUI 里做好的填充，可以在控制台读到：

```python
doc = App.ActiveDocument
pad = doc.getObject("Pad")          # 名称以模型树为准
print(pad.Length)
pad.Length = 12                     # 单位 mm
doc.recompute()
```

草图约束：

```python
sk = doc.getObject("Sketch")
# 约束列表：sk.Constraints
# 按名称（需先在草图里给约束命名）：
# sk.setDatum("Length", 100)
doc.recompute()
```

## 保存与导出

```python
doc.saveAs("/tmp/DemoPlate.FCStd")
# 导出 STEP 需要 Import 模块
import Import
Import.export([doc.getObject("Plate")], "/tmp/DemoPlate.step")
```

路径按操作系统修改。无 GUI 的服务器上可用 `freecadcmd` 跑同一脚本。

## 宏

1. **宏 → 宏** → 新建，粘贴代码，保存到用户宏目录。
2. 可把宏拖到工具栏。
3. 只使用 `App` / `Part` / `Sketcher` 等模块；需要点选界面时才 `import FreeCADGui as Gui`。

## 和 Jupyter / 外部 Python

官方包把 `FreeCAD.so` 编进安装目录，系统 Python 不一定能 `import FreeCAD`。更稳妥：

- 用 FreeCAD 自带的 **Python 控制台 / 宏**；或
- `freecadcmd script.py`；或
- 插件管理器里的相关工具。

不要假设 `pip install freecad` 能得到完整 CAD 内核。

## 下一步

- 文档：[Python scripting](https://wiki.freecad.org/Python_scripting_tutorial)
- 对象文档：控制台里 `help(Part.makeBox)`、`dir(pad)`
- 复杂特征优先在 GUI 做一次，打开 **视图 → 面板 → 宏录制** 看生成的 Python，再改成自己的函数

下一章：[08 速查表与排错](08-cheatsheet.md)
