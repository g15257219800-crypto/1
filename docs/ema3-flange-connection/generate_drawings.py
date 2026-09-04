#!/usr/bin/env python3
"""Generate technical SVGs for Parker EMA3 to flange connection design."""

from pathlib import Path

OUT = Path(__file__).resolve().parent / "drawings"
OUT.mkdir(parents=True, exist_ok=True)


def svg(name: str, body: str, w: int = 960, h: int = 620) -> None:
    content = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
  <rect width="100%" height="100%" fill="#f7f4ea"/>
  <style>
    .t {{ font-family: "Noto Sans CJK SC", "Source Han Sans SC", "Noto Sans", sans-serif; fill: #1a1a1a; }}
    .dim {{ font-family: "Noto Sans", sans-serif; font-size: 12px; fill: #1a4a7a; }}
    .title {{ font-size: 20px; font-weight: 700; }}
    .sub {{ font-size: 13px; fill: #444; }}
    .note {{ font-size: 12px; fill: #333; }}
    .stroke {{ fill: none; stroke: #1a1a1a; stroke-width: 1.6; }}
    .thin {{ fill: none; stroke: #1a1a1a; stroke-width: 1.0; }}
    .hid {{ fill: none; stroke: #666; stroke-width: 0.9; stroke-dasharray: 5 3; }}
    .center {{ fill: none; stroke: #8a2f2f; stroke-width: 0.7; stroke-dasharray: 8 3 2 3; }}
    .diml {{ fill: none; stroke: #1a4a7a; stroke-width: 0.8; }}
    .fill-steel {{ fill: #c9c4b6; stroke: #1a1a1a; stroke-width: 1.4; }}
    .fill-body {{ fill: #8a8f7a; stroke: #1a1a1a; stroke-width: 1.4; }}
    .fill-cap {{ fill: #d4a017; stroke: #1a1a1a; stroke-width: 1.3; }}
    .fill-or {{ fill: #3d6b4f; stroke: #1a1a1a; stroke-width: 1.0; }}
    .fill-fluid {{ fill: #cfe6f2; stroke: #2a5f7a; stroke-width: 0.8; }}
    .fill-plate {{ fill: #b7c4c8; stroke: #1a1a1a; stroke-width: 1.4; }}
  </style>
  {body}
</svg>
"""
    (OUT / name).write_text(content, encoding="utf-8")
    print("wrote", name)


def overview() -> None:
    body = """
  <text class="t title" x="40" y="42">派克 EMA3 与法兰 — 四种连接方案</text>
  <text class="t sub" x="40" y="64">测压端统一为 M16×2 螺纹快接；油口端按法兰类型选型。推荐优先方案 A 或方案 C。</text>

  <!-- A -->
  <rect x="36" y="88" width="430" height="230" rx="8" fill="#fff" stroke="#1a1a1a"/>
  <text class="t" x="52" y="114" font-size="15" font-weight="700">方案 A  法兰本体径向油口（新制件首选）</text>
  <rect class="fill-steel" x="70" y="150" width="150" height="90"/>
  <rect class="fill-fluid" x="70" y="182" width="150" height="26"/>
  <rect class="fill-body" x="220" y="168" width="70" height="54"/>
  <circle class="fill-cap" cx="312" cy="195" r="16"/>
  <rect class="fill-or" x="214" y="176" width="8" height="38"/>
  <line class="center" x1="50" y1="195" x2="332" y2="195"/>
  <text class="t note" x="78" y="168">法兰颈 / 阀块</text>
  <text class="t note" x="228" y="160">EMA3</text>
  <text class="t note" x="292" y="160">防尘帽</text>
  <text class="t note" x="52" y="268">ISO 6149-1  M14×1.5 诊断油口  ·  EMA3/14X1.5ISO  ·  PN 630 bar</text>
  <text class="t note" x="52" y="288">密封：接头自带 O 形圈，压入 15° 锥面。不改主密封面。</text>

  <!-- C -->
  <rect x="490" y="88" width="430" height="230" rx="8" fill="#fff" stroke="#1a1a1a"/>
  <text class="t" x="506" y="114" font-size="15" font-weight="700">方案 C  测压隔板（不改原法兰）</text>
  <rect class="fill-steel" x="520" y="150" width="70" height="100"/>
  <rect class="fill-plate" x="590" y="165" width="90" height="70"/>
  <rect class="fill-steel" x="680" y="150" width="70" height="100"/>
  <rect class="fill-fluid" x="520" y="188" width="230" height="24"/>
  <rect class="fill-body" x="618" y="235" width="36" height="48"/>
  <circle class="fill-cap" cx="636" cy="300" r="12"/>
  <text class="t note" x="528" y="144">原法兰</text>
  <text class="t note" x="602" y="158">隔板</text>
  <text class="t note" x="692" y="144">对侧法兰</text>
  <text class="t note" x="506" y="268">夹在 ISO 6162 / SAE J518 连接面之间，侧面攻诊断油口。</text>
  <text class="t note" x="506" y="288">既有管路可加装，主密封仍用原法兰 O 形圈。</text>

  <!-- B -->
  <rect x="36" y="338" width="430" height="230" rx="8" fill="#fff" stroke="#1a1a1a"/>
  <text class="t" x="52" y="364" font-size="15" font-weight="700">方案 B  G1/4 ED 油口（国内现场常用）</text>
  <rect class="fill-steel" x="70" y="400" width="150" height="90"/>
  <rect class="fill-fluid" x="70" y="432" width="150" height="26"/>
  <polygon class="fill-body" points="220,418 290,430 290,470 220,482"/>
  <circle class="fill-cap" cx="312" cy="450" r="16"/>
  <text class="t note" x="52" y="518">ISO 1179-1 Type W  G1/4  ·  EMA3/1/4ED  ·  PN 630 bar</text>
  <text class="t note" x="52" y="538">密封：ED 弹性密封圈压在油口端面。攻丝简便，小法兰更易布置。</text>

  <!-- D -->
  <rect x="490" y="338" width="430" height="230" rx="8" fill="#fff" stroke="#1a1a1a"/>
  <text class="t" x="506" y="364" font-size="15" font-weight="700">方案 D  标准法兰转接头串联</text>
  <rect class="fill-steel" x="520" y="400" width="56" height="90"/>
  <polygon class="fill-plate" points="576,415 656,400 656,490 576,475"/>
  <rect class="fill-body" x="656" y="422" width="70" height="48"/>
  <circle class="fill-cap" cx="748" cy="446" r="14"/>
  <text class="t note" x="506" y="518">GFS / PFF-G 法兰转螺纹  →  三通或直接侧口  →  EMA3</text>
  <text class="t note" x="506" y="538">全部外购标准件，适合临时测压或无法机加的现场。</text>

  <text class="t note" x="40" y="592">选型口诀：新制法兰/阀块 → A；已有 ISO 6162 连接不想拆改本体 → C；现场只有 BSPP 丝锥 → B；全部用标准件、不机加 → D。</text>
"""
    svg("01-scheme-overview.svg", body)


def scheme_a() -> None:
    body = """
  <text class="t title" x="40" y="40">方案 A 装配图 — 法兰颈径向安装 EMA3</text>
  <text class="t sub" x="40" y="62">油口：ISO 6149-1 M14×1.5（诊断口优先规格）　接头：EMA3/14X1.5ISO　测压端：M16×2</text>

  <!-- flange body -->
  <rect class="fill-steel" x="80" y="120" width="280" height="200"/>
  <rect x="80" y="120" width="36" height="200" fill="#9a9588" stroke="#1a1a1a" stroke-width="1.4"/>
  <text class="t note" x="86" y="230" transform="rotate(-90 92 230)">法兰密封面</text>

  <!-- main bore -->
  <rect class="fill-fluid" x="80" y="198" width="280" height="44"/>
  <line class="center" x1="70" y1="220" x2="720" y2="220"/>
  <text class="t note" x="120" y="190">主管通径 DN</text>

  <!-- diagnostic boss -->
  <rect class="fill-steel" x="200" y="90" width="70" height="30"/>
  <text class="t note" x="208" y="84">诊断凸台</text>

  <!-- EMA3 body -->
  <rect class="fill-body" x="360" y="188" width="150" height="64"/>
  <polygon points="360,196 352,196 352,244 360,244" class="fill-or"/>
  <rect x="390" y="176" width="28" height="88" fill="#6e7460" stroke="#1a1a1a" stroke-width="1.3"/>
  <text class="t note" x="386" y="168">S1 对边 19</text>

  <!-- M16x2 end + cap -->
  <rect x="510" y="200" width="70" height="40" fill="#6e7460" stroke="#1a1a1a" stroke-width="1.3"/>
  <circle class="fill-cap" cx="610" cy="220" r="22"/>
  <circle cx="610" cy="220" r="10" class="thin"/>
  <text class="t note" x="500" y="188">M16×2</text>
  <text class="t note" x="590" y="188">金属防尘帽</text>

  <!-- connecting hole -->
  <rect class="fill-fluid" x="226" y="198" width="134" height="10"/>
  <text class="t note" x="250" y="270">连通孔 Ø7.5 与主管相交，去毛刺</text>

  <!-- dimensions -->
  <line class="diml" x1="360" y1="270" x2="510" y2="270"/>
  <text class="dim" x="400" y="288">L1 ≈ 39.5（样本）</text>
  <line class="diml" x1="80" y1="340" x2="360" y2="340"/>
  <text class="dim" x="160" y="358">法兰颈需容纳油口全螺纹 ≥ 11.5</text>

  <text class="t note" x="40" y="420">密封原理：接头颈部 O 形圈被压入油口 15° 锥面，螺纹只承受拉力，不参与密封。</text>
  <text class="t note" x="40" y="442">安装：润滑 O 形圈 → 用手旋入至接触 → 扭矩 35 N·m（钢件、ISO 6149-3 L 系列，润滑装配）。</text>
  <text class="t note" x="40" y="464">油口必须用 ISO 6149 成形刀具加工，禁止用普通 90° 沉孔代替 15° 密封锥面。</text>
  <text class="t note" x="40" y="486">凸台外径建议 ≥ Ø32，凸台高 ≥ 2；油口轴线与法兰螺栓错开，扳手空间按 S=19 预留。</text>
  <text class="t note" x="40" y="520">不适用：法兰颈壁厚不足以形成全螺纹 + 剩余壁；此时改用方案 C 隔板或方案 D 转接头。</text>
"""
    svg("02-scheme-a-hub-port.svg", body)


def iso_port() -> None:
    body = """
  <text class="t title" x="40" y="40">ISO 6149-1 诊断油口  M14×1.5 — 加工图</text>
  <text class="t sub" x="40" y="62">ISO 6149-1 将 M14×1.5 列为诊断油口优先规格。与 EMA3/14X1.5ISO 配对。</text>

  <!-- section view -->
  <polygon class="fill-steel" points="120,80 420,80 420,470 120,470 120,250 200,250 200,200 120,200"/>
  <!-- port cavity -->
  <path d="M120,200 L210,200 L210,208 L205,216 L205,320 L120,320 Z" class="fill-fluid"/>
  <!-- 15 deg approx: from d4=19.5 to d5=15.8 -->
  <line class="thin" x1="120" y1="200" x2="210" y2="200"/>
  <line class="thin" x1="210" y1="200" x2="210" y2="208"/>
  <line class="thin" x1="210" y1="208" x2="205" y2="216"/>
  <line class="thin" x1="205" y1="216" x2="205" y2="320"/>
  <line class="center" x1="80" y1="260" x2="480" y2="260"/>

  <!-- hatch -->
  <defs>
    <pattern id="hatch" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
      <line x1="0" y1="0" x2="0" y2="8" stroke="#7a7568" stroke-width="0.7"/>
    </pattern>
  </defs>
  <polygon points="120,80 420,80 420,200 210,200 210,208 205,216 205,320 120,320 120,470 420,470 420,500 90,500 90,80" fill="url(#hatch)" opacity="0.35"/>

  <!-- dimensions right -->
  <line class="diml" x1="430" y1="80" x2="430" y2="200"/>
  <text class="dim" x="438" y="150">端面</text>

  <line class="diml" x1="250" y1="200" x2="250" y2="208"/>
  <text class="dim" x="258" y="207">L1 ≥ 2.4 沉孔深</text>

  <line class="diml" x1="250" y1="208" x2="250" y2="216"/>
  <text class="dim" x="258" y="228">Z = 15° ±1° 密封锥</text>

  <line class="diml" x1="250" y1="216" x2="250" y2="320"/>
  <text class="dim" x="258" y="270">全螺纹 L4 ≥ 11.5</text>
  <text class="dim" x="258" y="288">底孔深按丝锥加长</text>

  <line class="diml" x1="120" y1="190" x2="210" y2="190"/>
  <text class="dim" x="130" y="182">d4 = Ø19.5  0/+0.1</text>

  <line class="diml" x1="80" y1="80" x2="80" y2="470"/>
  <text class="dim" x="40" y="90">宽型</text>
  <text class="dim" x="28" y="108">spotface</text>
  <text class="dim" x="22" y="126">d2 ≥ Ø25</text>
  <text class="dim" x="22" y="300">连通孔</text>
  <text class="dim" x="22" y="316">d3 ≈ Ø7.5</text>

  <!-- table -->
  <rect x="520" y="80" width="400" height="420" rx="6" fill="#fff" stroke="#1a1a1a"/>
  <text class="t" x="540" y="110" font-size="15" font-weight="700">M14×1.5 油口尺寸（mm）</text>
  <text class="t note" x="540" y="140">螺纹 d1×P　　M14×1.5-6H（ISO 261）</text>
  <text class="t note" x="540" y="164">宽型端面 d2　　≥ Ø25（带识别凸环）</text>
  <text class="t note" x="540" y="188">窄型端面 d2　　≥ Ø21（无凸环）</text>
  <text class="t note" x="540" y="212">连通孔 d3　　　Ø7.5（参考，可按流量改）</text>
  <text class="t note" x="540" y="236">密封孔 d4　　　Ø19.5  0 / +0.1</text>
  <text class="t note" x="540" y="260">锥底直径 d5　　Ø15.8  0 / +0.4</text>
  <text class="t note" x="540" y="284">沉孔深 L1　　　≥ 2.4</text>
  <text class="t note" x="540" y="308">底孔深 L2　　　约 14（平底丝锥）</text>
  <text class="t note" x="540" y="332">全螺纹 L4　　　≥ 11.5</text>
  <text class="t note" x="540" y="356">密封锥角 Z　　15° ±1°</text>
  <text class="t note" x="540" y="390">表面：密封锥与端面 Ra ≤ 1.6 μm</text>
  <text class="t note" x="540" y="414">螺纹：6H，去锐边，禁止磕碰密封锥</text>
  <text class="t note" x="540" y="438">刀具：ISO 6149 / SAE J2244 成形锪钻</text>
  <text class="t note" x="540" y="462">标识：零件上标注 METRIC 或 ISO 6149</text>
  <text class="t note" x="540" y="486">配对接头　EMA3/14X1.5ISO　PN 630 bar</text>
"""
    svg("03-iso6149-m14-port.svg", body, 960, 560)


def scheme_c() -> None:
    body = """
  <text class="t title" x="40" y="40">方案 C 装配图 — ISO 6162 测压隔板</text>
  <text class="t sub" x="40" y="62">隔板夹在两法兰之间。主密封仍用原法兰头 O 形圈；隔板两侧为平面。侧面安装 EMA3。</text>

  <!-- left flange head -->
  <rect class="fill-steel" x="80" y="110" width="70" height="220"/>
  <rect class="fill-or" x="142" y="170" width="8" height="100"/>
  <text class="t note" x="86" y="100">法兰头（带 O 形圈槽）</text>

  <!-- spacer -->
  <rect class="fill-plate" x="150" y="130" width="90" height="180"/>
  <text class="t note" x="162" y="122">测压隔板</text>
  <rect class="fill-fluid" x="80" y="200" width="250" height="40"/>

  <!-- right flange -->
  <rect class="fill-steel" x="240" y="110" width="90" height="220"/>
  <rect class="fill-or" x="240" y="170" width="8" height="100"/>
  <text class="t note" x="250" y="100">对侧法兰 / 油口垫</text>

  <!-- bolts -->
  <rect x="70" y="130" width="280" height="12" fill="#5c5c5c" stroke="#1a1a1a"/>
  <rect x="70" y="298" width="280" height="12" fill="#5c5c5c" stroke="#1a1a1a"/>
  <text class="t note" x="360" y="142">加长螺栓</text>
  <text class="t note" x="360" y="310">对角拧紧</text>

  <!-- EMA3 down -->
  <rect class="fill-body" x="172" y="310" width="46" height="80"/>
  <circle class="fill-cap" cx="195" cy="408" r="16"/>
  <text class="t note" x="226" y="360">EMA3</text>
  <text class="t note" x="226" y="378">M16×2</text>

  <!-- split clamps hint -->
  <text class="t note" x="80" y="450">FHS 对开法兰夹 + 4 条 12.9 级螺栓。隔板厚度计入螺栓长度：L = 原长 + t + 垫圈补偿。</text>
  <text class="t note" x="80" y="472">隔板两面平面度 0.03 / 100，Ra ≤ 1.6 μm，无划伤。O 形圈留在法兰头槽内，隔板不开槽（配置 C1）。</text>
  <text class="t note" x="80" y="494">若两侧都是平面油口垫，则隔板两面按 ISO 6162 开 O 形圈槽（配置 C2）。</text>
  <text class="t note" x="80" y="530">板厚 t ≥ 30（M14 ISO 6149）或 t ≥ 26（G1/4 ED），保证侧面 spotface 完整、全螺纹足够。</text>
  <text class="t note" x="80" y="552">测压口开在螺栓矩形的长边中点，避开螺栓头与对开夹。</text>
  <text class="t note" x="80" y="574">小通径 1/2″：优先 G1/4 ED 或把板厚做到 32，油口仍放长边。</text>
"""
    svg("04-scheme-c-spacer.svg", body)


def spacer_plate() -> None:
    body = """
  <text class="t title" x="40" y="36">测压隔板零件图（ISO 6162-1 Code 61 示例）</text>
  <text class="t sub" x="40" y="56">示意 DN25 / 1″。其余通径按附表改螺栓距与内孔。材料 42CrMo4 调质或 316L。</text>

  <!-- top view plate -->
  <rect class="fill-plate" x="80" y="90" width="280" height="220" rx="10"/>
  <circle class="fill-fluid" cx="220" cy="200" r="36"/>
  <circle class="thin" cx="140" cy="140" r="7"/>
  <circle class="thin" cx="300" cy="140" r="7"/>
  <circle class="thin" cx="140" cy="260" r="7"/>
  <circle class="thin" cx="300" cy="260" r="7"/>
  <line class="center" x1="220" y1="90" x2="220" y2="310"/>
  <line class="center" x1="80" y1="200" x2="360" y2="200"/>

  <!-- diagnostic port on long side -->
  <circle class="thin" cx="360" cy="200" r="14"/>
  <line class="hid" x1="256" y1="200" x2="360" y2="200"/>
  <text class="t note" x="368" y="196">测压口</text>
  <text class="t note" x="368" y="214">M14×1.5</text>

  <line class="diml" x1="140" y1="330" x2="300" y2="330"/>
  <text class="dim" x="190" y="348">a = 52.4（1″ Code 61）</text>
  <line class="diml" x1="60" y1="140" x2="60" y2="260"/>
  <text class="dim" x="18" y="206">b=26.2</text>
  <line class="diml" x1="80" y1="80" x2="360" y2="80"/>
  <text class="dim" x="170" y="74">外形 ≈ 72 × 62</text>

  <!-- side view -->
  <rect class="fill-plate" x="520" y="120" width="200" height="90"/>
  <rect class="fill-fluid" x="520" y="150" width="200" height="30"/>
  <rect class="fill-fluid" x="700" y="155" width="70" height="20"/>
  <text class="t note" x="520" y="110">侧视（厚度方向）</text>
  <line class="diml" x1="500" y1="120" x2="500" y2="210"/>
  <text class="dim" x="430" y="172">t = 32</text>
  <text class="t note" x="540" y="230">两面平面，无 O 形圈槽（配置 C1）</text>

  <!-- notes box -->
  <rect x="40" y="380" width="880" height="210" rx="6" fill="#fff" stroke="#1a1a1a"/>
  <text class="t" x="56" y="408" font-size="14" font-weight="700">加工与检验要点</text>
  <text class="t note" x="56" y="434">1. 内孔与法兰通径一致或略大 0.5 mm，锐边倒钝 R0.3，与侧孔相交处必须去毛刺。</text>
  <text class="t note" x="56" y="458">2. 四螺栓孔按 ISO 6162-1，孔距公差 ±0.25，与端面垂直度 0.1。</text>
  <text class="t note" x="56" y="482">3. 测压口用 ISO 6149 成形刀；轴线通过内孔中心，偏移 ≤ 0.2 mm。</text>
  <text class="t note" x="56" y="506">4. 密封面：两侧法兰贴合面 Ra ≤ 1.6 μm，平面度 0.03 mm，禁止贯穿划伤。</text>
  <text class="t note" x="56" y="530">5. 钢件表面镀锌无六价铬（与派克 CF 体系一致）或发黑；不锈钢酸洗钝化。</text>
  <text class="t note" x="56" y="554">6. 试压：隔板装配后按系统 1.5 倍工作压力保压，测压口用原装防尘帽拧紧。</text>
  <text class="t note" x="56" y="578">7. 螺栓强度 12.9，按对角、分步拧到 ISO 6162 规定扭矩；隔板加厚后复核螺栓工作长度。</text>
"""
    svg("05-spacer-plate.svg", body, 960, 620)


def scheme_d() -> None:
    body = """
  <text class="t title" x="40" y="40">方案 D / E — 标准件转接与管法兰焊接凸台</text>

  <rect x="36" y="70" width="430" height="250" rx="8" fill="#fff" stroke="#1a1a1a"/>
  <text class="t" x="52" y="98" font-size="15" font-weight="700">D1  法兰 → BSPP 内螺纹块  →  EMA3</text>
  <text class="t note" x="52" y="124">派克 PFF-G（SAE 四螺栓法兰 + G 内螺纹）</text>
  <text class="t note" x="52" y="146">再配变径 RI-ED 或直接选带 G1/4 侧口的阀块。</text>
  <text class="t note" x="52" y="176">D2  法兰 → EO 24°（GFS）→ 管路测压接头 GMA3</text>
  <text class="t note" x="52" y="198">GMA3 串在硬管中间，测压端仍为 M16×2，与 EMA3 同一软管体系。</text>
  <text class="t note" x="52" y="228">D3  法兰软管接头旁路三通（ORFS / 37°）+ 诊断接头</text>
  <text class="t note" x="52" y="250">派克诊断三通可适配 EMA3 / PD。适合软管总成。</text>
  <text class="t note" x="52" y="282">特点：零机加。压力等级取转接头与 EMA3 的较低值。</text>

  <rect x="490" y="70" width="430" height="250" rx="8" fill="#fff" stroke="#1a1a1a"/>
  <text class="t" x="506" y="98" font-size="15" font-weight="700">方案 E  GB / HG 管法兰焊接凸台</text>
  <rect class="fill-steel" x="530" y="130" width="160" height="28"/>
  <rect class="fill-steel" x="560" y="158" width="100" height="70"/>
  <circle class="fill-body" cx="700" cy="193" r="22"/>
  <circle class="fill-cap" cx="748" cy="193" r="14"/>
  <rect class="fill-fluid" x="560" y="180" width="140" height="16"/>
  <text class="t note" x="506" y="250">在法兰颈或短节上焊接 ISO 6149 螺纹凸台</text>
  <text class="t note" x="506" y="270">（或预制带测压口的法兰短节）。</text>
  <text class="t note" x="506" y="294">焊后热处理按母材；油口焊后再精加工。</text>

  <text class="t note" x="40" y="360">压力匹配：EMA3 最高 630 bar，但法兰侧常为 PN16/25/40 或 SAE Code 61（210–350 bar）/ Code 62（420 bar）。</text>
  <text class="t note" x="40" y="382">整个测压支路的许用压力 = min(法兰额定、转接头额定、EMA3 该螺纹规格额定、软管 SMA3 额定)。</text>
  <text class="t note" x="40" y="404">带压插接上限 400 bar（EMA3 螺纹耦合）。工作中防尘帽必须拧紧，振动场合用自锁金属帽。</text>
  <text class="t note" x="40" y="440">禁止：锥管螺纹（NPT/PT）作为高压液压诊断口；禁止把 EMA3 直接焊在法兰上；禁止密封胶代替 O 形圈 / ED 圈。</text>
  <text class="t note" x="40" y="462">介质：矿物油液压液与 NBR 匹配；磷酸酯 / 高温选 71 不锈钢 + FKM。</text>
"""
    svg("06-scheme-d-e.svg", body, 960, 500)


def main() -> None:
    overview()
    scheme_a()
    iso_port()
    scheme_c()
    spacer_plate()
    scheme_d()


if __name__ == "__main__":
    main()
