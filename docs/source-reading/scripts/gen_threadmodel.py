# -*- coding: utf-8 -*-
import os
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'images')

W = 1480

BLUE = "#2a78d6"       # receive/decode side
BLUE_D = "#184f95"
ORANGE = "#eb6834"     # detect/output side
VIOLET = "#4a3aa7"     # queue / conduit
GRAY = "#e1e0d9"
GRAY_D = "#898781"
INK = "#0b0b0b"
SUB = "#52514e"

parts = []
parts.append(None)  # svg 头，等算出 H 再填
parts.append('<filter id="softshadow" x="-30%" y="-30%" width="160%" height="160%"><feDropShadow dx="0" dy="3" stdDeviation="4" flood-color="#0b0b0b" flood-opacity="0.16"/></filter>')
parts.append(None)  # 背景，等算出 H 再填

parts.append(f'<text x="{W/2}" y="50" text-anchor="middle" font-size="28" font-weight="700" fill="{INK}">线程模型：TmModule 怎么变成一条正在跑的流水线</text>')
parts.append(f'<text x="{W/2}" y="80" text-anchor="middle" font-size="15" fill="{SUB}">workers / single / autofp 三种排班方式的拓扑差异</text>')

def box(x, y, w, h, fill, title, sub, tcolor=INK, radius=12, stroke=None, dashed=False):
    dash = ' stroke-dasharray="6,4"' if dashed else ''
    st = f' stroke="{stroke}" stroke-width="1.5"' if stroke else ' stroke="rgba(11,11,11,0.08)" stroke-width="1"'
    s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}"{st}{dash} filter="url(#softshadow)"/>'
    if sub:
        s += f'<text x="{x+w/2}" y="{y+h/2-4}" text-anchor="middle" font-size="15.5" font-weight="700" fill="{tcolor}">{title}</text>'
        s += f'<text x="{x+w/2}" y="{y+h/2+16}" text-anchor="middle" font-size="11.5" fill="{tcolor}">{sub}</text>'
    else:
        s += f'<text x="{x+w/2}" y="{y+h/2+5}" text-anchor="middle" font-size="15.5" font-weight="700" fill="{tcolor}">{title}</text>'
    return s

def stack(x, y, w, h, n=2, d=8, radius=16):
    """在框后面画几层错位的虚线框，表示"同样的东西有好几份"。"""
    s = ''
    for i in range(n, 0, -1):
        s += f'<rect x="{x+d*i}" y="{y+d*i}" width="{w}" height="{h}" rx="{radius}" fill="#f3f2ed" stroke="#c3c2b7" stroke-width="1.2" stroke-dasharray="6,4"/>'
    return s

def label(x, y, text, size=13, color=SUB, anchor="start", weight="400"):
    return f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" fill="{color}" font-weight="{weight}">{text}</text>'

def harrow(x1, y, x2, color=GRAY_D):
    s = f'<line x1="{x1}" y1="{y}" x2="{x2-7}" y2="{y}" stroke="{color}" stroke-width="2"/>'
    s += f'<polygon points="{x2-7},{y-5} {x2},{y} {x2-7},{y+5}" fill="{color}"/>'
    return s

def varrow(x, y1, y2, color=GRAY_D):
    s = f'<line x1="{x}" y1="{y1}" x2="{x}" y2="{y2-7}" stroke="{color}" stroke-width="2"/>'
    s += f'<polygon points="{x-5},{y2-7} {x+5},{y2-7} {x},{y2}" fill="{color}"/>'
    return s

# ---- Section A: TmModule -> TmSlot -> ThreadVars mini flow ----
ay = 115
parts.append(label(60, ay+2, "① 一份说明书，发给工人后变成上岗单", 15, INK, weight="700"))
row_y = ay + 20
bw, bh = 190, 64
x1 = 60
parts.append(box(x1, row_y, bw, bh, GRAY, "TmModule", "岗位说明书（全局唯一）", INK))
x2 = x1 + bw + 170
parts.append(harrow(x1+bw, row_y+bh/2, x2))
parts.append(label((x1+bw+x2)/2, row_y+bh/2-10, "TmSlotSetFuncAppend()", 11.5, SUB, "middle"))
parts.append(box(x2, row_y, bw, bh, BLUE, "TmSlot", "某工人的上岗单", "#ffffff"))
x3 = x2 + bw + 170
parts.append(harrow(x2+bw, row_y+bh/2, x3))
parts.append(label((x2+bw+x3)/2, row_y+bh/2-10, "挂到 tm_slots 链表", 11.5, SUB, "middle"))
parts.append(box(x3, row_y, bw, bh, VIOLET, "ThreadVars", "一个工人的档案卡", "#ffffff"))
parts.append(label(x3+bw+24, row_y+bh/2+5, "一个 ThreadVars 可挂一串 TmSlot（slot_next 链）", 12.5, SUB))

divider_y = row_y + bh + 34
parts.append(f'<line x1="40" y1="{divider_y}" x2="{W-40}" y2="{divider_y}" stroke="#e1e0d9" stroke-width="1.5"/>')

# ---- Section B: workers lane ----
by = divider_y + 40
parts.append(label(60, by, "② workers（single 是它在“1 线程 / 1 网卡”下的特例）", 15, INK, weight="700"))

lane_y = by + 24
thread_w, thread_h = 900, 110
tx = 60
parts.append(stack(tx, lane_y, thread_w, thread_h))
parts.append(box(tx, lane_y, thread_w, thread_h, "#fcfcfb", "", "", stroke="#c3c2b7", dashed=True, radius=16))
parts.append(label(tx+18, lane_y+22, "每个线程一个 ThreadVars，驱动方式 pktacqloop", 12.5, SUB))
parts.append(label(tx+thread_w+44, lane_y+thread_h/2+2, "× N 个线程", 22, INK, weight="700"))
parts.append(label(tx+thread_w+44, lane_y+thread_h/2+28, "W#01 … W#N，每个都一模一样", 12.5, SUB))

slot_w, slot_h = 175, 56
slot_y = lane_y + 36
slots = [("ReceiveAFP", BLUE), ("DecodeAFP", BLUE), ("FlowWorker", ORANGE), ("RespondReject", ORANGE)]
sx = tx + 30
for i, (name, color) in enumerate(slots):
    parts.append(box(sx, slot_y, slot_w, slot_h, color, name, None, "#ffffff", radius=10))
    if i != len(slots)-1:
        parts.append(harrow(sx+slot_w, slot_y+slot_h/2, sx+slot_w+30))
    sx += slot_w + 30

parts.append(label(tx+thread_w/2, lane_y+thread_h+36, "in / out 都是 packetpool，包全程不离开这个线程", 12, SUB, "middle"))

# ---- Section C: autofp lane ----
cy = lane_y + thread_h + 76
parts.append(label(60, cy, "③ autofp：两组线程，中间用 pickup 队列接力", 15, INK, weight="700"))

lane2_y = cy + 24
group_w, group_h = 420, 110
gx1 = 60
parts.append(stack(gx1, lane2_y, group_w, group_h))
parts.append(box(gx1, lane2_y, group_w, group_h, "#fcfcfb", "", "", stroke="#c3c2b7", dashed=True, radius=16))
parts.append(label(gx1+18, lane2_y+22, "抓包线程 RX#01 … RX#M，驱动方式 pktacqloop", 12.5, SUB))
parts.append(label(gx1+group_w/2, lane2_y+group_h+38, "× M(由 af-packet 的 threads 配置决定)", 12, SUB, "middle"))
s2y = lane2_y + 36
s2x = gx1 + 24
for i, (name, color) in enumerate([("ReceiveAFP", BLUE), ("DecodeAFP", BLUE)]):
    parts.append(box(s2x, s2y, 170, slot_h, color, name, None, "#ffffff", radius=10))
    if i == 0:
        parts.append(harrow(s2x+170, s2y+slot_h/2, s2x+170+26))
    s2x += 170 + 26

# queue box
qx = gx1 + group_w + 50
qw, qh = 200, 110
parts.append(harrow(gx1+group_w, lane2_y+group_h/2, qx, VIOLET))
for i in (2, 1):
    parts.append(f'<rect x="{qx+8*i}" y="{lane2_y+8*i}" width="{qw}" height="{qh}" rx="12" fill="#8a7fd0" stroke="#ffffff" stroke-width="1.5"/>')
parts.append(box(qx, lane2_y, qw, qh, VIOLET, "pickup1 … pickupN", "每个处理线程一条队列", "#ffffff"))
parts.append(label(qx+qw/2+8, lane2_y+qh+38, "按 flow_hash % N 选队列，同一条流永远进同一条", 12, SUB, "middle"))

# second group
gx2 = qx + qw + 50
parts.append(harrow(qx+qw, lane2_y+group_h/2, gx2, VIOLET))
parts.append(stack(gx2, lane2_y, group_w-40, group_h))
parts.append(box(gx2, lane2_y, group_w-40, group_h, "#fcfcfb", "", "", stroke="#c3c2b7", dashed=True, radius=16))
parts.append(label(gx2+18, lane2_y+22, "处理线程 W#01 … W#N，驱动方式 varslot", 12.5, SUB))
parts.append(label(gx2+(group_w-40)/2, lane2_y+group_h+38, "× N(默认按 CPU 核数算)", 12, SUB, "middle"))
s3y = lane2_y + 36
s3x = gx2 + 24
for i, (name, color) in enumerate([("FlowWorker", ORANGE), ("RespondReject", ORANGE)]):
    parts.append(box(s3x, s3y, 155, slot_h, color, name, None, "#ffffff", radius=10))
    if i == 0:
        parts.append(harrow(s3x+155, s3y+slot_h/2, s3x+155+20))
    s3x += 155 + 20

H = lane2_y + group_h + 70
parts[0] = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="-apple-system, \'Segoe UI\', \'PingFang SC\', \'Microsoft YaHei\', sans-serif">'
parts[2] = f'<rect x="0" y="0" width="{W}" height="{H}" fill="#fcfcfb"/>'
parts.append('</svg>')

with open(os.path.join(OUT_DIR, 'suricata-thread-model.svg'), 'w', encoding='utf-8') as f:
    f.write(''.join(parts))
print("gx2 end approx:", gx2 + group_w - 40)
