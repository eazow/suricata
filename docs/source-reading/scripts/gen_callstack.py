# -*- coding: utf-8 -*-
"""一个包在线程里的调用栈：pktacqloop 与 varslot 两种驱动方式，在 TmThreadsSlotVarRun() 会合。
函数名与行号均对照 suricata-8.0.7 源码核实。"""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'images', 'suricata-callstack.svg')

W = 1480
INK, SUB, MUTED = "#0b0b0b", "#52514e", "#898781"
MONO = "'SF Mono', Menlo, Consolas, monospace"
STYLE = {  # 填充色, 边框色, 函数名颜色
    "main":  ("#e1e0d9", "#c3c2b7", INK),
    "cap":   ("#e3eefb", "#6da7ec", "#184f95"),
    "disp":  ("#ecebf7", "#8a7fd0", "#4a3aa7"),
    "merge": ("#fff1e8", "#eb6834", "#c24e1f"),
    "mod":   ("#ffffff", "#f3b394", "#c24e1f"),
    "queue": ("#ecebf7", "#8a7fd0", "#4a3aa7"),
}
INDENT, ROW_GAP = 34, 10

parts = []


def text(x, y, s, size, color, anchor="start", weight="400", family=None):
    fam = f' font-family="{family}"' if family else ''
    return (f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" '
            f'font-weight="{weight}" fill="{color}"{fam}>{s}</text>')


def arrow_head(x, y, direction, color):
    if direction == "right":
        pts = f"{x-8},{y-5} {x},{y} {x-8},{y+5}"
    else:  # left
        pts = f"{x+8},{y-5} {x},{y} {x+8},{y+5}"
    return f'<polygon points="{pts}" fill="{color}"/>'


def column(x0, width, y0, rows):
    """画一列调用栈，返回每行的 (x, y, w, h)。rows: (level, name, loc, desc, style)。"""
    boxes = []
    y = y0
    for level, name, loc, desc, style in rows:
        x = x0 + level * INDENT
        w = width - level * INDENT
        h = 52 if desc else 38
        fill, stroke, ncolor = STYLE[style]
        sw = 2 if style == "merge" else 1.2
        parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="9" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
        ny = y + (21 if desc else 24)
        parts.append(text(x + 14, ny, name, 13.5, ncolor, weight="700", family=MONO))
        if loc:
            parts.append(text(x + w - 12, ny, loc, 11, MUTED, "end", family=MONO))
        if desc:
            parts.append(text(x + 14, y + 41, desc, 11.5, SUB))
        boxes.append((x, y, w, h, level))
        y += h + ROW_GAP
    # 父子连线：竖线从父框左侧往下，横线接到子框
    for i, (x, y, w, h, level) in enumerate(boxes):
        if level == 0:
            continue
        for j in range(i - 1, -1, -1):
            px, py, pw, ph, plevel = boxes[j]
            if plevel == level - 1:
                lx = px + 14
                parts.append(f'<path d="M {lx} {py+ph} L {lx} {y+h/2} L {x} {y+h/2}" fill="none" stroke="#c3c2b7" stroke-width="1.5"/>')
                break
    return boxes


parts.append(text(W / 2, 48, "一个包在线程里的调用栈", 26, INK, "middle", "700"))
parts.append(text(W / 2, 76, "两种驱动方式，最后都汇到同一个 for 循环：同一个包，在同一个线程的调用栈上走完整条工位链", 14, SUB, "middle"))

LX, RX, CW = 50, 780, 650
HEAD_Y = 118
parts.append(text(LX, HEAD_Y, "pktacqloop", 17, INK, weight="800", family=MONO))
parts.append(text(LX + 118, HEAD_Y, "workers 线程 / autofp 抓包线程", 13, SUB))
parts.append(text(RX, HEAD_Y, "varslot", 17, INK, weight="800", family=MONO))
parts.append(text(RX + 86, HEAD_Y, "autofp 处理线程", 13, SUB))

left_rows = [
    (0, "TmThreadsSlotPktAcqLoop()", "tm-threads.c:310", "线程主函数：初始化各 slot → 等放行 → 调用链头的 PktAcqLoop", "main"),
    (1, "ReceiveAFPLoop()", "source-af-packet.c:1300", "链头 ReceiveAFP 的抓包循环，开头先记下 ptv->slot = s->slot_next", "cap"),
    (2, "AFPReadFromRing()", "source-af-packet.c:887", "从环形缓冲区取一帧，装进 Packet", "cap"),
    (3, "TmThreadsSlotProcessPkt()", "tm-threads.h:195", "把包交给 ptv->slot，也就是链上剩下的工位", "disp"),
    (4, "TmThreadsSlotVarRun()", "tm-threads.c:133", "for 循环，顺着 slot_next 逐个调用 SlotFunc", "merge"),
    (5, "DecodeAFP()", "source-af-packet.c:2771", "", "mod"),
    (5, "FlowWorker()", "flow-worker.c:559", "", "mod"),
    (5, "RespondRejectFunc()", "respond-reject.c:65", "", "mod"),
    (4, "tv->tmqh_out(tv, p)", "", "workers：还回包池　autofp：按流哈希塞进 pickup 队列", "queue"),
]
lb = column(LX, CW, HEAD_Y + 22, left_rows)

# 右列往下错开，让两个 TmThreadsSlotVarRun() 对齐在同一高度
merge_y = lb[4][1]
right_rows = [
    (0, "TmThreadsSlotVar()", "tm-threads.c:410", "线程主函数：初始化各 slot → 等放行 → while 循环取包", "main"),
    (1, "tv->tmqh_in(tv)", "tmqh-flow.c:98", "TmqhInputFlow：从自己那条 pickup 队列取一个包", "queue"),
    (1, "TmThreadsSlotVarRun()", "tm-threads.c:133", "同一个函数：顺着 slot_next 逐个调用 SlotFunc", "merge"),
    (2, "FlowWorker()", "flow-worker.c:559", "", "mod"),
    (2, "RespondRejectFunc()", "respond-reject.c:65", "", "mod"),
    (1, "tv->tmqh_out(tv, p)", "tmqh-packetpool.c:305", "TmqhOutputPacketpool：还回包池", "queue"),
]
right_y0 = merge_y - (52 + ROW_GAP) * 2
rb = column(RX, CW, right_y0, right_rows)

# 会合处的高亮带
band_y = merge_y - 8
parts.insert(0, f'<rect x="{LX-24}" y="{band_y}" width="{RX+CW-LX+48}" height="68" rx="12" fill="#fde3d3" opacity="0.55"/>')

# 左列循环箭头：tmqh_out → 回到 AFPReadFromRing
qx, qy, qw, qh, _ = lb[8]
ax, ay, aw, ah, _ = lb[2]
loop_x = LX - 22
parts.append(f'<path d="M {qx} {qy+qh/2} L {loop_x} {qy+qh/2} L {loop_x} {ay+ah/2} L {ax-2} {ay+ah/2}" fill="none" stroke="{MUTED}" stroke-width="1.6" stroke-dasharray="5,4"/>')
parts.append(arrow_head(ax, ay + ah / 2, "right", MUTED))
parts.append(f'<text x="{loop_x-8}" y="{(qy+ay)/2}" text-anchor="middle" font-size="11.5" fill="{MUTED}" transform="rotate(-90 {loop_x-8} {(qy+ay)/2})">抓下一个包</text>')

# 右列循环箭头：tmqh_out → 回到 tmqh_in
ox, oy, ow, oh, _ = rb[5]
ix, iy, iw, ih, _ = rb[1]
rloop_x = RX + CW + 22
parts.append(f'<path d="M {ox+ow} {oy+oh/2} L {rloop_x} {oy+oh/2} L {rloop_x} {iy+ih/2} L {ix+iw+2} {iy+ih/2}" fill="none" stroke="{MUTED}" stroke-width="1.6" stroke-dasharray="5,4"/>')
parts.append(arrow_head(ix + iw, iy + ih / 2, "left", MUTED))
parts.append(f'<text x="{rloop_x+8}" y="{(oy+iy)/2}" text-anchor="middle" font-size="11.5" fill="{MUTED}" transform="rotate(90 {rloop_x+8} {(oy+iy)/2})">取下一个包</text>')

# autofp：左列 tmqh_out 经 pickup 队列 → 右列 tmqh_in
cross_x = (LX + CW + RX) / 2
parts.append(f'<path d="M {qx+qw} {qy+qh/2} L {cross_x} {qy+qh/2} L {cross_x} {iy+ih/2} L {ix-2} {iy+ih/2}" fill="none" stroke="#8a7fd0" stroke-width="1.8" stroke-dasharray="6,4"/>')
parts.append(arrow_head(ix, iy + ih / 2, "right", "#8a7fd0"))
cross_mid = (qy + qh / 2 + iy + ih / 2) / 2
parts.append(f'<text x="{cross_x-9}" y="{cross_mid}" text-anchor="middle" font-size="11.5" fill="#4a3aa7" transform="rotate(-90 {cross_x-9} {cross_mid})">autofp：经 pickup 队列交给处理线程</text>')

bottom = max(qy + qh, oy + oh) + 40
parts.append(text(LX, bottom, "省略了错误处理，以及解码拆出隧道内层包时的伪包处理。", 12, MUTED))

H = bottom + 28
head = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'font-family="-apple-system, \'Segoe UI\', \'PingFang SC\', \'Microsoft YaHei\', sans-serif">'
        f'<rect x="0" y="0" width="{W}" height="{H}" fill="#fcfcfb"/>')

with open(OUT, 'w', encoding='utf-8') as f:
    f.write(head + ''.join(parts) + '</svg>')
print('wrote', OUT, 'H =', H)
