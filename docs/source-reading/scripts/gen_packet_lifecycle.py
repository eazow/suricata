# -*- coding: utf-8 -*-
"""一个 Packet 的一生(AF_PACKET，TPACKET_V2，workers 模式)：从环形缓冲区借帧、从包池借 Packet，处理完各自归还。
函数名均对照 suricata-8.0.7 源码核实。"""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'images', 'suricata-packet-lifecycle.svg')

W, H = 1480, 760
INK, SUB, MUTED = "#0b0b0b", "#52514e", "#898781"
MONO = "'SF Mono', Menlo, Consolas, monospace"
BLUE, BLUE_L = "#2a78d6", "#e3eefb"
ORANGE, ORANGE_L = "#eb6834", "#fff1e8"
VIOLET, VIOLET_L = "#4a3aa7", "#ecebf7"
GRAY, GRAY_L = "#898781", "#e1e0d9"

parts = []


def text(x, y, s, size, color, anchor="start", weight="400", family=None):
    fam = f' font-family="{family}"' if family else ''
    return (f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" '
            f'font-weight="{weight}" fill="{color}"{fam}>{s}</text>')


def varrow(x, y1, y2, color, dashed=False, width=2):
    """竖直箭头，从 y1 指向 y2。"""
    dash = ' stroke-dasharray="6,4"' if dashed else ''
    d = 1 if y2 > y1 else -1
    s = f'<line x1="{x}" y1="{y1}" x2="{x}" y2="{y2 - 8*d}" stroke="{color}" stroke-width="{width}"{dash}/>'
    s += f'<polygon points="{x-5},{y2-8*d} {x+5},{y2-8*d} {x},{y2}" fill="{color}"/>'
    return s


def harrow(x1, y, x2, color):
    s = f'<line x1="{x1}" y1="{y}" x2="{x2-8}" y2="{y}" stroke="{color}" stroke-width="2"/>'
    s += f'<polygon points="{x2-8},{y-5} {x2},{y} {x2-8},{y+5}" fill="{color}"/>'
    return s


parts.append(text(W / 2, 46, "一个 Packet 的一生", 26, INK, "middle", "700"))
parts.append(text(W / 2, 74, "AF_PACKET(TPACKET_V2)、workers 模式：从环里借一帧、从包池借一个 Packet，处理完各自归还", 14, SUB, "middle"))

# ---- 中间：五个步骤 ----
STEP_Y, STEP_H, STEP_W, STEP_GAP = 330, 118, 236, 40
step_x0 = (W - (5 * STEP_W + 4 * STEP_GAP)) / 2
steps = [
    ("① 等待与取帧", ["PacketPoolWait()：确保包池有空包", "poll() 等到帧状态变成", "TP_STATUS_USER"], BLUE, BLUE_L),
    ("② 取一个 Packet", ["PacketGetFromQueueOrAlloc()", "先从本线程包池取，", "取不到才临时 malloc"], VIOLET, VIOLET_L),
    ("③ 装配", ["PacketSetData()：ext_pkt 指向帧", "填 ts / livedev / datalink", "ReleasePacket = AFPReleasePacket"], ORANGE, ORANGE_L),
    ("④ 流水线处理", ["TmThreadsSlotProcessPkt()", "DecodeAFP → FlowWorker → …", "(第 2 篇)"], GRAY, "#f3f2ed"),
    ("⑤ 释放", ["TmqhOutputPacketpool()", "最后调用 p->ReleasePacket(p)", "也就是 AFPReleasePacket()"], ORANGE, ORANGE_L),
]
centers = []
for i, (title, lines, color, fill) in enumerate(steps):
    x = step_x0 + i * (STEP_W + STEP_GAP)
    parts.append(f'<rect x="{x}" y="{STEP_Y}" width="{STEP_W}" height="{STEP_H}" rx="12" fill="{fill}" stroke="{color}" stroke-width="1.6"/>')
    parts.append(text(x + 16, STEP_Y + 30, title, 15.5, color if color != GRAY else INK, weight="700"))
    for j, ln in enumerate(lines):
        parts.append(text(x + 16, STEP_Y + 56 + j * 20, ln, 11.5, SUB))
    if i < len(steps) - 1:
        parts.append(harrow(x + STEP_W, STEP_Y + STEP_H / 2, x + STEP_W + STEP_GAP, GRAY))
    centers.append(x + STEP_W / 2)

# ---- 上方：环形缓冲区 ----
RING_X, RING_Y, RING_W, RING_H = 60, 106, W - 120, 132
parts.append(f'<rect x="{RING_X}" y="{RING_Y}" width="{RING_W}" height="{RING_H}" rx="14" fill="#fcfcfb" stroke="{BLUE}" stroke-width="1.6"/>')
parts.append(text(RING_X + 20, RING_Y + 28, "AF_PACKET 环形缓冲区", 15.5, BLUE, weight="700"))
parts.append(text(RING_X + 200, RING_Y + 28, "PACKET_RX_RING + mmap：内核和 Suricata 共用同一块内存，每一格(帧)靠 tp_status 交接", 12, SUB))

CELL_W, CELL_H, CELL_GAP = 78, 50, 10
n_cells = int((RING_W - 40 + CELL_GAP) // (CELL_W + CELL_GAP))
cells_x0 = RING_X + (RING_W - (n_cells * CELL_W + (n_cells - 1) * CELL_GAP)) / 2
cell_y = RING_Y + 54
KERNEL = ("内核", "KERNEL", "#f3f2ed", "#c3c2b7", MUTED)
USER = ("就绪", "USER", BLUE_L, "#6da7ec", BLUE)
LENT = ("借出中", "USER", ORANGE_L, ORANGE, ORANGE)
BACK = ("已归还", "KERNEL", "#f3f2ed", "#c3c2b7", MUTED)


def cell_at(x):
    for i in range(n_cells):
        cx = cells_x0 + i * (CELL_W + CELL_GAP)
        if cx - CELL_GAP / 2 <= x <= cx + CELL_W + CELL_GAP / 2:
            return i
    return None


special = {cell_at(centers[0]): USER, cell_at(centers[2]): LENT, cell_at(centers[4]): BACK}
pattern = [KERNEL, USER, USER, KERNEL]
for i in range(n_cells):
    label_cn, label_en, fill, stroke, tcolor = special.get(i, pattern[i % len(pattern)])
    cx = cells_x0 + i * (CELL_W + CELL_GAP)
    parts.append(f'<rect x="{cx}" y="{cell_y}" width="{CELL_W}" height="{CELL_H}" rx="7" fill="{fill}" stroke="{stroke}" stroke-width="1.3"/>')
    parts.append(text(cx + CELL_W / 2, cell_y + 22, label_cn, 12, tcolor, "middle", "700"))
    parts.append(text(cx + CELL_W / 2, cell_y + 39, label_en, 9.5, tcolor, "middle", family=MONO))

ring_bottom = RING_Y + RING_H
# 环 → ①：内核写好一帧
parts.append(varrow(centers[0], ring_bottom, STEP_Y, BLUE))
parts.append(text(centers[0] + 8, ring_bottom + 44, "内核写好一帧", 11.5, BLUE))
# ③ → 环：ext_pkt 指向这一帧(零拷贝)
parts.append(varrow(centers[2], STEP_Y, ring_bottom, ORANGE, dashed=True))
parts.append(text(centers[2] + 8, ring_bottom + 36, "ext_pkt 指向这一帧", 11.5, ORANGE, weight="700"))
parts.append(text(centers[2] + 8, ring_bottom + 54, "零拷贝：数据一直留在环里", 11.5, ORANGE))
# ⑤ → 环：帧还给内核
parts.append(varrow(centers[4], STEP_Y, ring_bottom, ORANGE))
parts.append(text(centers[4] - 10, ring_bottom + 36, "AFPReleaseDataFromRing()", 11.5, ORANGE, "end", "700", MONO))
parts.append(text(centers[4] - 10, ring_bottom + 54, "tp_status 设回 KERNEL，这一格还给内核", 11.5, ORANGE, "end"))

# ---- 下方：包池 ----
POOL_Y, POOL_H = STEP_Y + STEP_H + 92, 126
parts.append(f'<rect x="{RING_X}" y="{POOL_Y}" width="{RING_W}" height="{POOL_H}" rx="14" fill="#fcfcfb" stroke="{VIOLET}" stroke-width="1.6"/>')
parts.append(text(RING_X + 20, POOL_Y + POOL_H - 20, "本线程的包池", 15.5, VIOLET, weight="700"))
parts.append(text(RING_X + 132, POOL_Y + POOL_H - 20, "thread_local 的 thread_pkt_pool，线程启动时预分配 max-pending-packets 个 Packet(默认 1024)，同线程取还不加锁", 12, SUB))
pool_cell_y = POOL_Y + 22
used = {cell_at(centers[1]): ("取出", VIOLET, VIOLET_L), cell_at(centers[4]): ("放回", VIOLET, VIOLET_L)}
for i in range(n_cells):
    cx = cells_x0 + i * (CELL_W + CELL_GAP)
    lbl, stroke, fill = used.get(i, ("Packet", "#c3c2b7", "#f3f2ed"))
    tcolor = VIOLET if i in used else MUTED
    parts.append(f'<rect x="{cx}" y="{pool_cell_y}" width="{CELL_W}" height="{CELL_H}" rx="7" fill="{fill}" stroke="{stroke}" stroke-width="1.3"/>')
    parts.append(text(cx + CELL_W / 2, pool_cell_y + 30, lbl, 12, tcolor, "middle", "700"))

step_bottom = STEP_Y + STEP_H
# 包池 → ②：取出
parts.append(varrow(centers[1], POOL_Y, step_bottom, VIOLET))
parts.append(text(centers[1] + 8, step_bottom + 50, "PacketPoolGetPacket()", 11.5, VIOLET, weight="700", family=MONO))
# ⑤ → 包池：放回
parts.append(varrow(centers[4], step_bottom, POOL_Y, VIOLET))
parts.append(text(centers[4] - 10, step_bottom + 50, "PacketPoolReturnPacket()", 11.5, VIOLET, "end", "700", MONO))

foot_y = POOL_Y + POOL_H + 36
parts.append(text(RING_X, foot_y, "释放之前，这一帧一直被 Packet 借着，内核不能往里写新数据；所以环的大小(ring-size)至少要装得下所有在途的包。", 12.5, SUB))
parts.append(text(RING_X, foot_y + 22, "TPACKET_V3 按块(block)读取和归还，一块里有多个包，整块处理完才还给内核；图中以逐帧交接的 V2 为例。", 12.5, MUTED))

H = foot_y + 48
head = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'font-family="-apple-system, \'Segoe UI\', \'PingFang SC\', \'Microsoft YaHei\', sans-serif">'
        f'<rect x="0" y="0" width="{W}" height="{H}" fill="#fcfcfb"/>')

with open(OUT, 'w', encoding='utf-8') as f:
    f.write(head + ''.join(parts) + '</svg>')
print('wrote', OUT, 'H =', H)
