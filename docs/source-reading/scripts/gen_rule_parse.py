# -*- coding: utf-8 -*-
"""一条规则从文本到结构：规则头 → Signature 字段；每个选项 → 对应关键字的 Setup()；
解析阶段存在 init_data 的链表里，SigMatchPrepare() 再转成检测时用的数组和检查引擎。
函数名均对照 suricata-8.0.7 源码核实。"""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'images', 'suricata-rule-parse.svg')

W = 1480
INK, SUB, MUTED = "#0b0b0b", "#52514e", "#898781"
MONO = "'SF Mono', Menlo, Consolas, monospace"
BLUE, BLUE_L, BLUE_T = "#2a78d6", "#e3eefb", "#1f5fae"
ORANGE, ORANGE_L, ORANGE_T = "#eb6834", "#fff1e8", "#a8431c"
VIOLET, VIOLET_L = "#4a3aa7", "#ecebf7"
GRAY, GRAY_L = "#898781", "#f3f2ed"
ROSE, ROSE_L, ROSE_T = "#c2407a", "#fbeaf1", "#9e2f60"

parts = []


def text(x, y, s, size, color, anchor="start", weight="400", family=None):
    fam = f' font-family="{family}"' if family else ''
    s = s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    return (f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" '
            f'font-weight="{weight}" fill="{color}"{fam} xml:space="preserve">{s}</text>')


def rect(x, y, w, h, stroke, fill, rx=10, dashed=False, sw=1.5):
    dash = ' stroke-dasharray="6,4"' if dashed else ''
    parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{dash}/>')


def arrow(x1, y1, x2, y2, color):
    if x1 == x2:
        s = 1 if y2 > y1 else -1
        parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2-8*s}" stroke="{color}" stroke-width="1.8"/>')
        parts.append(f'<polygon points="{x2-5},{y2-8*s} {x2+5},{y2-8*s} {x2},{y2}" fill="{color}"/>')
    else:
        s = 1 if x2 > x1 else -1
        parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2-8*s}" y2="{y2}" stroke="{color}" stroke-width="1.8"/>')
        parts.append(f'<polygon points="{x2-8*s},{y2-5} {x2-8*s},{y2+5} {x2},{y2}" fill="{color}"/>')


parts.append(text(W / 2, 46, "一条规则从文本到结构", 26, INK, "middle", "700"))
parts.append(text(W / 2, 74, "规则头填进 Signature 的字段；每个选项交给对应关键字的 Setup()；解析完再转成检测时用的结构", 14, SUB, "middle"))

# ---- 规则文本，分段着色 ----
RY = 104
rect(40, RY, W - 80, 56, GRAY, "#fcfcfb")
segs = [
    ("alert http any any -> any any", BLUE_T, BLUE_L),
    (" (", INK, None),
    ('msg:"Example";', GRAY, None),
    (" ", INK, None),
    ("flow:established,to_server;", VIOLET, VIOLET_L),
    (" ", INK, None),
    ("http.uri;", ORANGE_T, ORANGE_L),
    (" ", INK, None),
    ('content:"/admin"; nocase;', ROSE_T, ROSE_L),
    (" ", INK, None),
    ("sid:1000001; rev:1;", GRAY, None),
    (")", INK, None),
]
CW = 8.4   # 等宽字符宽度(14px)
tx = 64
for s, color, fill in segs:
    w = len(s) * CW
    if fill:
        parts.append(f'<rect x="{tx-2}" y="{RY+14}" width="{w+4}" height="28" rx="5" fill="{fill}"/>')
    parts.append(text(tx, RY + 34, s, 14, color, family=MONO, weight="700" if fill else "400"))
    tx += w

# ---- 第二行：三栏 ----
R2 = 200
COLW = (W - 80 - 40) / 3
cols_x = [40 + i * (COLW + 20) for i in range(3)]

# 栏 1：规则头
x = cols_x[0]
rect(x, R2, COLW, 250, BLUE, "#fcfcfb")
parts.append(text(x + 16, R2 + 28, "① 规则头 → Signature 字段", 15, BLUE_T, weight="700"))
parts.append(text(x + 16, R2 + 46, "SigParseBasics()", 12, MUTED, family=MONO))
rows = [("alert", "s->action"), ("http", "s->alproto = HTTP，打上应用层标志"), ("any any", "源地址、源端口"), ("->", "方向"), ("any any", "目的地址、目的端口"), ("msg / sid / rev", "s->msg、s->id、s->rev(选项里的)")]
for i, (k, v) in enumerate(rows):
    yy = R2 + 80 + i * 28
    parts.append(text(x + 16, yy, k, 12.5, BLUE_T, weight="700", family=MONO))
    parts.append(text(x + 172, yy, v, 12, SUB))

# 栏 2：选项 → Setup()
x = cols_x[1]
rect(x, R2, COLW, 250, VIOLET, "#fcfcfb")
parts.append(text(x + 16, R2 + 28, "② 选项 → 关键字的 Setup()", 15, VIOLET, weight="700"))
parts.append(text(x + 16, R2 + 46, "SigParseOptions()，在 sigmatch_table 里按名字查", 12, MUTED))
steps = [
    ("flow", VIOLET, "新建 SigMatch，加到 MATCH 链表"),
    ("http.uri", ORANGE_T, "不产生 SigMatch：把\"当前链表\"切到 http_uri"),
    ("content", ROSE_T, "新建 SigMatch，加到\"当前链表\""),
    ("nocase", ROSE_T, "不产生 SigMatch：改前一个 content"),
]
for i, (k, c, v) in enumerate(steps):
    yy = R2 + 84 + i * 40
    parts.append(text(x + 16, yy, k, 12.5, c, weight="700", family=MONO))
    parts.append(text(x + 106, yy, v, 12, SUB))

# 栏 3：init_data
x = cols_x[2]
rect(x, R2, COLW, 250, GRAY, GRAY_L)
parts.append(text(x + 16, R2 + 28, "③ 解析阶段的存放：init_data", 15, INK, weight="700"))
parts.append(text(x + 16, R2 + 46, "临时结构，解析完就释放", 12, MUTED))
# MATCH 链表
parts.append(text(x + 16, R2 + 82, "smlists[MATCH]", 12.5, INK, weight="700", family=MONO))
rect(x + 170, R2 + 64, 150, 30, VIOLET, VIOLET_L, rx=6, sw=1.2)
parts.append(text(x + 245, R2 + 84, "flow", 12.5, VIOLET, "middle", "700", MONO))
parts.append(text(x + 16, R2 + 112, "固定链表还有 PMATCH、POSTMATCH 等", 11.5, MUTED))
# buffers
parts.append(text(x + 16, R2 + 150, "buffers[http_uri]", 12.5, INK, weight="700", family=MONO))
rect(x + 170, R2 + 132, 150, 30, ROSE, ROSE_L, rx=6, sw=1.2)
parts.append(text(x + 245, R2 + 152, '"/admin" nocase', 12, ROSE_T, "middle", "700", MONO))
parts.append(text(x + 16, R2 + 180, "每个缓冲区一条链表", 11.5, MUTED))
parts.append(text(x + 16, R2 + 214, "没指定缓冲区时，content 默认", 11.5, SUB))
parts.append(text(x + 16, R2 + 233, "进 PMATCH，检查包载荷", 11.5, SUB))

arrow(cols_x[0] + COLW, R2 + 125, cols_x[1], R2 + 125, GRAY)
arrow(cols_x[1] + COLW, R2 + 125, cols_x[2], R2 + 125, GRAY)

# ---- 第三行：SigMatchPrepare 之后 ----
R3 = R2 + 300
arrow(W / 2, R2 + 250, W / 2, R3, ORANGE)
parts.append(text(W / 2 + 12, R2 + 280, "全部规则读完，SigGroupBuild() 里调用 SigMatchPrepare()", 12.5, ORANGE_T, weight="700"))
rect(40, R3, W - 80, 150, ORANGE, ORANGE_L)
parts.append(text(60, R3 + 30, "④ 检测时用的结构", 15, ORANGE_T, weight="700"))
# 左：sm_arrays
parts.append(text(60, R3 + 66, "s->sm_arrays[MATCH]", 12.5, INK, weight="700", family=MONO))
rect(250, R3 + 48, 120, 30, VIOLET, VIOLET_L, rx=6, sw=1.2)
parts.append(text(310, R3 + 68, "flow", 12.5, VIOLET, "middle", "700", MONO))
parts.append(text(60, R3 + 96, "链表转成数组：检测时顺序遍历，", 11.5, SUB))
parts.append(text(60, R3 + 114, "每项调用关键字的 Match()", 11.5, SUB))
# 右：app_inspect
ax = 540
parts.append(text(ax, R3 + 66, "s->app_inspect", 12.5, INK, weight="700", family=MONO))
eng = [("http_uri · HTTP/1 · to_server · 进度 ≥ LINE(请求行)", '"/admin"'), ("http_uri · HTTP/2 · to_server", '"/admin"')]
for i, (e, c) in enumerate(eng):
    yy = R3 + 48 + i * 42
    rect(ax + 150, yy, 470, 30, ORANGE, "#fcfcfb", rx=6, sw=1.2)
    parts.append(text(ax + 164, yy + 20, e, 12, ORANGE_T, weight="700"))
    arrow(ax + 620, yy + 15, ax + 650, yy + 15, ORANGE)
    rect(ax + 650, yy, 150, 30, ROSE, ROSE_L, rx=6, sw=1.2)
    parts.append(text(ax + 725, yy + 20, c, 12, ROSE_T, "middle", "700", MONO))
parts.append(text(ax, R3 + 134, "按缓冲区挂上注册好的检查引擎；同一个 http.uri 规则，对 HTTP/1 和 HTTP/2 都生效", 11.5, SUB))

H = R3 + 150 + 34
head = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'font-family="-apple-system, \'Segoe UI\', \'PingFang SC\', \'Microsoft YaHei\', sans-serif">'
        f'<rect x="0" y="0" width="{W}" height="{H}" fill="#fcfcfb"/>')
with open(OUT, 'w', encoding='utf-8') as f:
    f.write(head + ''.join(parts) + '</svg>')
print('wrote', OUT, 'H =', H)
