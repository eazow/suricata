# -*- coding: utf-8 -*-
"""应用层框架：协议识别(PM → PP → PE) → 调用解析器(成功 / 数据不够 / 出错) → 事务从开始到释放。
函数名均对照 suricata-8.0.7 源码核实。"""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'images', 'suricata-applayer.svg')

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
    return (f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" '
            f'font-weight="{weight}" fill="{color}"{fam}>{s}</text>')


def box(x, y, w, h, title, lines, stroke, fill, tcolor, dashed=False, title_mono=False):
    dash = ' stroke-dasharray="6,4"' if dashed else ''
    parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{fill}" stroke="{stroke}" stroke-width="1.5"{dash}/>')
    parts.append(text(x + 14, y + 25, title, 14, tcolor, weight="700", family=MONO if title_mono else None))
    for i, ln in enumerate(lines):
        parts.append(text(x + 14, y + 47 + i * 19, ln, 11.5, SUB))
    return x, y, w, h


def arrow(pts, color, label=None, at=None, anchor="start", dashed=False):
    dash = ' stroke-dasharray="6,4"' if dashed else ''
    (x1, y1), (x2, y2) = pts[-2], pts[-1]
    if x1 == x2:
        s = 1 if y2 > y1 else -1
        end, head = (x2, y2 - 8 * s), f"{x2-5},{y2-8*s} {x2+5},{y2-8*s} {x2},{y2}"
    else:
        s = 1 if x2 > x1 else -1
        end, head = (x2 - 8 * s, y2), f"{x2-8*s},{y2-5} {x2-8*s},{y2+5} {x2},{y2}"
    d = "M " + " L ".join(f"{x} {y}" for x, y in pts[:-1]) + f" L {end[0]} {end[1]}"
    parts.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="1.8"{dash}/>')
    parts.append(f'<polygon points="{head}" fill="{color}"/>')
    if label:
        parts.append(text(at[0], at[1], label, 11.5, SUB, anchor, "700"))


parts.append(text(W / 2, 46, "应用层框架：先认出协议，再交给解析器，解析出一个个事务", 25, INK, "middle", "700"))
parts.append(text(W / 2, 74, "以 HTTP 为例；每个协议在启动时注册特征串、探测函数和一组解析回调，框架按协议号查表调用", 14, SUB, "middle"))

# ---- 第一行：入口 + 协议识别 ----
entry = box(40, 110, 250, 104, "AppLayerHandleTCPData()", ["Stream 引擎交来一段", "已经拼好、已被 ACK 的数据"], GRAY, GRAY_L, INK, title_mono=True)

det = box(360, 100, 700, 172, "协议还不知道：协议识别", [], BLUE, "#fcfcfb", BLUE_T)
steps = [
    ("① PM 特征串", ["MPM 一次搜所有协议的特征", "HTTP：开头是 GET␣ / POST␣ …", "或 HTTP/1.1(响应方向)"]),
    ("② PP 按端口探测", ["按端口挑出可能的协议，", "调用它的探测函数试一试", "例：DNS 默认端口 53"]),
    ("③ PE 期望", ["别的连接事先登记好的", "例：FTP 协商出的", "数据连接"]),
]
sx = 376
for i, (t, ls) in enumerate(steps):
    parts.append(f'<rect x="{sx}" y="136" width="210" height="118" rx="8" fill="{BLUE_L}" stroke="{BLUE}" stroke-width="1.2"/>')
    parts.append(text(sx + 12, 158, t, 13, BLUE_T, weight="700"))
    for j, ln in enumerate(ls):
        parts.append(text(sx + 12, 180 + j * 19, ln, 11.5, SUB))
    if i < 2:
        arrow([(sx + 210, 195), (sx + 228, 195)], BLUE)
    sx += 228

known = box(1130, 110, 310, 104, "认出来了：f->alproto", ["记在 Flow 上，这条流以后", "不再识别，直接解析", "(STARTTLS 这类协议切换会重新识别)"], BLUE, BLUE_L, BLUE_T)

arrow([(entry[0] + entry[2], 162), (det[0], 162)], GRAY, "未知", (entry[0] + entry[2] + 35, 152), "middle")
arrow([(det[0] + det[2], 162), (known[0], 162)], BLUE)

# ---- 第二行：调用解析器 + 三种结果 ----
R2 = 320
parse = box(40, R2, 420, 128, "AppLayerParserParse()", ["按 (协议号, 应用层协议) 查出注册的回调，", "第一次先 StateAlloc() 建状态，挂到 f->alstate；", "再调用这个方向的 Parser[方向]：", "HTTP 是 HTPHandleRequestData() → Rust 版 libhtp"], VIOLET, VIOLET_L, VIOLET, title_mono=True)
# 入口 → 解析(已知)
arrow([(entry[0] + 60, entry[1] + entry[3]), (entry[0] + 60, R2)], VIOLET, "已知", (entry[0] + 70, entry[1] + entry[3] + 40))
# 认出 → 解析
arrow([(known[0] + known[2] / 2, known[1] + known[3]), (known[0] + known[2] / 2, 292), (parse[0] + parse[2] - 80, 292), (parse[0] + parse[2] - 80, R2)], BLUE)

res_x = 540
results = [
    ("成功", ["这段数据处理完了"], VIOLET, VIOLET_L, VIOLET),
    ("数据不够", ["返回 consumed / needed，needed 写进", "TCP 流的 data_required，攒够再调"], ORANGE, ORANGE_L, ORANGE_T),
    ("出错 / 不收缺口", ["StreamTcpDisableAppLayer()：", "这条流不再做应用层解析"], ROSE, ROSE_L, ROSE_T),
]
rw, rgap = 280, 20
for i, (t, ls, st, fl, tc) in enumerate(results):
    rx = res_x + i * (rw + rgap)
    box(rx, R2 + 14, rw, 100, t, ls, st, fl, tc)
arrow([(parse[0] + parse[2], R2 + 64), (res_x, R2 + 64)], VIOLET)

# ---- 第三行：事务 ----
R3 = R2 + 190
parts.append(text(40, R3 - 14, "解析的产物：事务(transaction)，一问一答算一个", 14, INK, weight="700"))
prog = ["NOT_STARTED", "LINE", "HEADERS", "BODY", "COMPLETE"]
px = 40
for i, s in enumerate(prog):
    pw = 150
    fill = BLUE if s == "COMPLETE" else BLUE_L
    tc = "#ffffff" if s == "COMPLETE" else BLUE_T
    parts.append(f'<rect x="{px}" y="{R3}" width="{pw}" height="42" rx="8" fill="{fill}" stroke="{BLUE}" stroke-width="1.2"/>')
    parts.append(text(px + pw / 2, R3 + 26, s, 12, tc, "middle", "700", MONO))
    if i < len(prog) - 1:
        arrow([(px + pw, R3 + 21), (px + pw + 20, R3 + 21)], BLUE)
    px += pw + 20
parts.append(text(40, R3 + 64, "HTTP 请求方向的进度(响应方向同理)；两个方向都到 COMPLETE，事务才算完成", 11.5, SUB))

use = box(px + 10, R3 - 30, 300, 100, "完成之后", ["检测：按事务检查 HTTP 字段(第 8、9 篇)", "日志：写出一条 http 事件(第 10 篇)"], ORANGE, ORANGE_L, ORANGE_T)
arrow([(px - 20, R3 + 21), (use[0], R3 + 21)], ORANGE)
free = box(use[0] + use[2] + 20, R3 - 30, W - 40 - (use[0] + use[2] + 20), 100, "释放", ["检测和日志都处理过，", "TransactionsCleanup()", "才把它释放"], GRAY, GRAY_L, INK)
arrow([(use[0] + use[2], R3 + 21), (free[0], R3 + 21)], GRAY)

H = R3 + 110
head = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'font-family="-apple-system, \'Segoe UI\', \'PingFang SC\', \'Microsoft YaHei\', sans-serif">'
        f'<rect x="0" y="0" width="{W}" height="{H}" fill="#fcfcfb"/>')
with open(OUT, 'w', encoding='utf-8') as f:
    f.write(head + ''.join(parts) + '</svg>')
print('wrote', OUT, 'H =', H)
