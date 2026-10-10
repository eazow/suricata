# -*- coding: utf-8 -*-
"""一条 Flow 的一生：从备用池取出 → 在流表里随包更新状态 → 过期 → 两条回收路线 → 写 flow 日志、清空、还回备用池。
函数名与默认值均对照 suricata-8.0.7 源码及默认配置核实。"""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'images', 'suricata-flow-lifecycle.svg')

W = 1480
INK, SUB, MUTED = "#0b0b0b", "#52514e", "#898781"
MONO = "'SF Mono', Menlo, Consolas, monospace"
BLUE, BLUE_L = "#2a78d6", "#e3eefb"
ORANGE, ORANGE_L = "#eb6834", "#fff1e8"
VIOLET, VIOLET_L = "#4a3aa7", "#ecebf7"
GRAY, GRAY_L = "#898781", "#f3f2ed"
RED, RED_L = "#c0392b", "#fbe9e7"

parts = []


def text(x, y, s, size, color, anchor="start", weight="400", family=None):
    fam = f' font-family="{family}"' if family else ''
    return (f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" '
            f'font-weight="{weight}" fill="{color}"{fam}>{s}</text>')


def box(x, y, w, h, title, lines, color, fill, dashed=False, title_family=None):
    dash = ' stroke-dasharray="6,4"' if dashed else ''
    parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{fill}" stroke="{color}" stroke-width="1.6"{dash}/>')
    parts.append(text(x + 16, y + 28, title, 15, color, weight="700", family=title_family))
    for i, ln in enumerate(lines):
        parts.append(text(x + 16, y + 52 + i * 20, ln, 12, SUB))
    return (x, y, w, h)


def arrow(points, color, dashed=False, label=None, label_at=None, anchor="start"):
    dash = ' stroke-dasharray="6,4"' if dashed else ''
    d = "M " + " L ".join(f"{x} {y}" for x, y in points[:-1])
    (x1, y1), (x2, y2) = points[-2], points[-1]
    # 最后一段缩短 8px 给箭头留位置
    if x1 == x2:
        s = 1 if y2 > y1 else -1
        end = (x2, y2 - 8 * s)
        head = f"{x2-5},{y2-8*s} {x2+5},{y2-8*s} {x2},{y2}"
    else:
        s = 1 if x2 > x1 else -1
        end = (x2 - 8 * s, y2)
        head = f"{x2-8*s},{y2-5} {x2-8*s},{y2+5} {x2},{y2}"
    d += f" L {end[0]} {end[1]}"
    parts.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="1.8"{dash}/>')
    parts.append(f'<polygon points="{head}" fill="{color}"/>')
    if label:
        lx, ly = label_at
        parts.append(text(lx, ly, label, 11.5, color, anchor, "700"))


parts.append(text(W / 2, 46, "一条 Flow 的一生", 26, INK, "middle", "700"))
parts.append(text(W / 2, 74, "从备用池取出，在流表里随包更新状态，过期后经两条路线之一回收，最后写 flow 日志、清空，还回备用池", 14, SUB, "middle"))

# ---- 第一行 ----
pool = box(40, 110, 250, 132, "备用池", ["线程私有的 spare_queue(不加锁)", "全局备用池：启动时预分配", "flow.prealloc 个(默认 10000)"], GRAY, GRAY_L)

table = box(390, 110, 640, 170, "流表里：一条活跃的 Flow", [], BLUE, "#fcfcfb")
# 状态条
chips = [("NEW", "TCP 60 秒"), ("ESTABLISHED", "TCP 600 秒"), ("CLOSED", "TCP 60 秒")]
cx = 410
for i, (st, to) in enumerate(chips):
    cw = 170
    parts.append(f'<rect x="{cx}" y="150" width="{cw}" height="56" rx="9" fill="{BLUE_L}" stroke="{BLUE}" stroke-width="1.3"/>')
    parts.append(text(cx + cw / 2, 174, st, 13, BLUE, "middle", "700", MONO))
    parts.append(text(cx + cw / 2, 195, "超时 " + to, 11.5, SUB, "middle"))
    if i < len(chips) - 1:
        arrow([(cx + cw, 178), (cx + cw + 36, 178)], BLUE)
    cx += cw + 36
parts.append(text(410, 232, "每来一个包：lastts = 包的时间，按方向累加包数、字节数", 12, SUB))
parts.append(text(410, 254, "状态一变，FlowUpdateState() 就重新计算 timeout_policy", 12, SUB))

expire = box(1110, 110, 330, 132, "过期了", ["lastts + timeout_policy", "早于当前包的时间", "(用的是包的时间戳，不是系统时钟)"], ORANGE, ORANGE_L)

arrow([(pool[0] + pool[2], 176), (table[0], 176)], GRAY, label="FlowGetNew()", label_at=(pool[0] + pool[2] + 40, 166), anchor="middle")
arrow([(table[0] + table[2], 176), (expire[0], 176)], ORANGE)

# ---- 第二行：两条回收路线 ----
ROW2 = 340
worker = box(390, ROW2, 330, 112, "① worker 线程顺手清理", ["查流表时路过、发现超时，移出哈希桶", "放进本线程的工作队列，", "由 CheckWorkQueue() 收尾"], VIOLET, VIOLET_L)
mgr = box(780, ROW2, 330, 112, "② FlowManager 巡检", ["每秒扫至少 10% 的哈希桶", "紧急模式下每 250 毫秒扫完整张表", "超时的流移出哈希桶"], VIOLET, VIOLET_L)
rec = box(1170, ROW2, 270, 112, "FlowRecycler", ["专门的回收线程", "从回收队列里成批取流"], VIOLET, VIOLET_L)
flush = box(780, ROW2 + 150, 330, 92, "TCP 流还有没处理完的数据？", ["FlowSendToLocalThread() 交回所属 worker，", "用伪包把剩下的数据冲刷一遍"], VIOLET, "#fcfcfb", dashed=True)

ex_mid = expire[0] + expire[2] / 2
# 过期 → ①、②
arrow([(ex_mid - 60, expire[1] + expire[3]), (ex_mid - 60, 300), (worker[0] + worker[2] / 2, 300), (worker[0] + worker[2] / 2, ROW2)], VIOLET)
arrow([(mgr[0] + mgr[2] / 2, 300), (mgr[0] + mgr[2] / 2, ROW2)], VIOLET)
# ② → FlowRecycler
arrow([(mgr[0] + mgr[2], ROW2 + 56), (rec[0], ROW2 + 56)], VIOLET, label="无残留", label_at=(mgr[0] + mgr[2] + 30, ROW2 + 46), anchor="middle")
# ② → 冲刷(虚线)
arrow([(mgr[0] + mgr[2] / 2, ROW2 + mgr[3]), (mgr[0] + mgr[2] / 2, flush[1])], VIOLET, dashed=True, label="有", label_at=(mgr[0] + mgr[2] / 2 + 10, ROW2 + mgr[3] + 24))
# 冲刷 → ①(交回 worker)
arrow([(flush[0], flush[1] + flush[3] / 2), (worker[0] + worker[2] / 2, flush[1] + flush[3] / 2), (worker[0] + worker[2] / 2, ROW2 + worker[3])], VIOLET, dashed=True)

# ---- 第三行：收尾 ----
ROW3 = ROW2 + 290
done = box(390, ROW3, 1050, 92, "收尾：两条路线都走到这里", ["OutputFlowLog() 写一条 EVE flow 日志：开始/结束时间、两个方向的包数和字节数、结束原因", "FlowClearMemory() 释放 TCP 会话、应用层状态等挂在 Flow 上的东西，然后还回备用池"], ORANGE, ORANGE_L)
arrow([(worker[0] + 70, ROW2 + worker[3]), (worker[0] + 70, ROW3)], ORANGE)
arrow([(rec[0] + rec[2] / 2, ROW2 + rec[3]), (rec[0] + rec[2] / 2, ROW3)], ORANGE)
# 收尾 → 备用池
back_x = 358
arrow([(done[0], ROW3 + 46), (back_x, ROW3 + 46), (back_x, 215), (pool[0] + pool[2], 215)], GRAY, label="还回备用池", label_at=(back_x - 8, ROW3 + 36), anchor="end")

# ---- 左下：紧急模式 ----
emerg = box(40, ROW2, 290, 150, "内存超过 flow.memcap", ["进入紧急模式：", "· 换成更短的紧急超时", "· 唤醒 FlowManager 加紧回收", "· FlowGetUsedFlow() 抢一条旧流"], RED, RED_L)
arrow([(pool[0] + pool[2] / 2 - 60, pool[1] + pool[3]), (pool[0] + pool[2] / 2 - 60, ROW2)], RED, dashed=True, label="池空且超上限", label_at=(pool[0] + pool[2] / 2 - 50, pool[1] + pool[3] + 34))

H = ROW3 + 92 + 40
head = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'font-family="-apple-system, \'Segoe UI\', \'PingFang SC\', \'Microsoft YaHei\', sans-serif">'
        f'<rect x="0" y="0" width="{W}" height="{H}" fill="#fcfcfb"/>')
with open(OUT, 'w', encoding='utf-8') as f:
    f.write(head + ''.join(parts) + '</svg>')
print('wrote', OUT, 'H =', H)
