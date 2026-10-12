# -*- coding: utf-8 -*-
"""规则分组与预过滤：启动时按方向/协议/端口把规则分组，每组用快速模式建一个 MPM；
运行时找到规则组 → MPM 一次搜出候选 → 只细查候选。函数名与默认值均对照 suricata-8.0.7 源码核实。"""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'images', 'suricata-detect-flow.svg')

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
            f'font-weight="{weight}" fill="{color}"{fam}>{s}</text>')


def box(x, y, w, h, title, lines, stroke, fill, tcolor, mono_title=False):
    parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>')
    parts.append(text(x + 14, y + 25, title, 14, tcolor, weight="700", family=MONO if mono_title else None))
    for i, ln in enumerate(lines):
        parts.append(text(x + 14, y + 47 + i * 19, ln, 11.5, SUB))
    return x, y, w, h


def harrow(x1, x2, y, color, label=None):
    parts.append(f'<line x1="{x1}" y1="{y}" x2="{x2-8}" y2="{y}" stroke="{color}" stroke-width="1.8"/>')
    parts.append(f'<polygon points="{x2-8},{y-5} {x2-8},{y+5} {x2},{y}" fill="{color}"/>')
    if label:
        parts.append(text((x1 + x2) / 2, y - 8, label, 11, SUB, "middle", "700"))


parts.append(text(W / 2, 46, "几万条规则一起跑：先分组，再预过滤，只细查少数几条", 25, INK, "middle", "700"))
parts.append(text(W / 2, 74, "上：启动时 SigGroupBuild() 建好规则组和 MPM；下：每个包在运行时走一遍", 14, SUB, "middle"))

# ---- 上：建组 ----
TOP = 104
parts.append(text(40, TOP + 4, "启动时：建规则组", 15, INK, weight="700"))
rules = box(40, TOP + 18, 250, 150, "全部规则(几万条)", ["先排序：pass > drop > reject > alert，", "再看 flowbits 依赖、优先级；", "排序后分配内部编号 iid"], GRAY, GRAY_L, INK)

grp_x = 360
parts.append(f'<rect x="{grp_x}" y="{TOP+18}" width="560" height="150" rx="10" fill="#fcfcfb" stroke="{BLUE}" stroke-width="1.5"/>')
parts.append(text(grp_x + 14, TOP + 43, "按 方向 × 协议 × 服务端端口 分组", 14, BLUE_T, weight="700"))
parts.append(text(grp_x + 14, TOP + 63, "RulesGroupByPorts()：TCP/UDP 按端口；其他协议按协议号", 11.5, SUB))
groups = [("to_server · TCP · 80", "HTTP 规则 + any 端口规则"), ("to_server · TCP · 443", "TLS 规则 + any 端口规则"), ("to_server · UDP · 53", "DNS 规则 + any 端口规则"), ("……", "medium：最多 40 / 20 组")]
for i, (g, d) in enumerate(groups):
    gx = grp_x + 14 + (i % 2) * 272
    gy = TOP + 78 + (i // 2) * 42
    parts.append(f'<rect x="{gx}" y="{gy}" width="260" height="34" rx="6" fill="{BLUE_L}" stroke="{BLUE}" stroke-width="1.1"/>')
    parts.append(text(gx + 10, gy + 15, g, 11.5, BLUE_T, weight="700", family=MONO))
    parts.append(text(gx + 10, gy + 29, d, 10.5, SUB))

mpm = box(990, TOP + 18, 450, 150, "每个组：用快速模式建 MPM", ["每条规则挑一个 content 当快速模式：", "  显式 fast_pattern 优先；否则在优先级最高的", "  缓冲区里挑最长的，一样长比模式强度", "按缓冲区各建一个 MPM(Hyperscan 或 Aho-Corasick)"], ORANGE, ORANGE_L, ORANGE_T)
harrow(rules[0] + rules[2], grp_x, TOP + 93, GRAY)
harrow(grp_x + 560, 990, TOP + 93, GRAY)

# ---- 下：运行时 ----
R2 = TOP + 230
parts.append(text(40, R2 - 10, "运行时：一个包", 15, INK, weight="700"))
steps = [
    ("① 找规则组", ["方向 + 协议 + 服务端端口查表；", "查到后缓存在 Flow 上", "(sgh_toserver / sgh_toclient)"], BLUE, BLUE_L, BLUE_T),
    ("② 预过滤", ["MPM 在载荷、缓冲区上", "一次搜出所有快速模式；", "没有快速模式的规则直接算候选"], ORANGE, ORANGE_L, ORANGE_T),
    ("③ 整理候选", ["命中的规则编号排序、去重", "→ match_array", "顺序就是规则的优先顺序"], VIOLET, VIOLET_L, VIOLET),
    ("④ 逐条细查", ["规则头(协议、端口、地址、flow)", "→ 其余条件逐个调 Match()", "全部满足：产生告警"], ROSE, ROSE_L, ROSE_T),
]
sw, sg = 320, 33
for i, (t, ls, st, fl, tc) in enumerate(steps):
    sx = 40 + i * (sw + sg)
    box(sx, R2, sw, 112, t, ls, st, fl, tc)
    if i < 3:
        harrow(sx + sw, sx + sw + sg, R2 + 56, GRAY)

# 漏斗数量
R3 = R2 + 150
nums = [("几万条", 40), ("这一组的几千条", 40 + sw + sg), ("命中快速模式的几十条", 40 + 2 * (sw + sg)), ("真正告警的 0 ~ 几条", 40 + 3 * (sw + sg))]
for label, x in nums:
    parts.append(text(x + sw / 2, R3, label, 12.5, INK, "middle", "700"))
parts.append(text(W / 2, R3 + 26, "(数量是示意，取决于规则集和流量)", 11, MUTED, "middle"))

# 事务检查
R4 = R3 + 52
box(40, R4, W - 80, 92, "⑤ 应用层事务：同样先预过滤再细查，并且受事务进度约束", ["DetectRunTx() 逐个事务：在 http_uri 这类缓冲区上跑 MPM 得到候选；检查引擎要求的进度还没到，就先停下，", "把检查到一半的状态存进事务的 de_state，等事务进度推进了再接着查(第 7、8 篇的事务进度在这里起作用)"], VIOLET, "#fcfcfb", VIOLET)

H = R4 + 92 + 30
head = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'font-family="-apple-system, \'Segoe UI\', \'PingFang SC\', \'Microsoft YaHei\', sans-serif">'
        f'<rect x="0" y="0" width="{W}" height="{H}" fill="#fcfcfb"/>')
with open(OUT, 'w', encoding='utf-8') as f:
    f.write(head + ''.join(parts) + '</svg>')
print('wrote', OUT, 'H =', H)
