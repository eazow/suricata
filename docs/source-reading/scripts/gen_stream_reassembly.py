# -*- coding: utf-8 -*-
"""TCP 重组示意：一个方向上，段按序号放进红黑树、数据拷进流式缓冲区；
IDS 模式下，只有被对方 ACK 的部分才交给应用层，ACK 了却没抓到的部分作为缺口(gap)通知应用层。
概念示意图，序号为举例；函数名与默认行为对照 suricata-8.0.7 源码核实。"""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'images', 'suricata-stream-reassembly.svg')

W = 1480
INK, SUB, MUTED = "#0b0b0b", "#52514e", "#898781"
MONO = "'SF Mono', Menlo, Consolas, monospace"
BLUE, BLUE_L = "#2a78d6", "#e3eefb"
ORANGE, ORANGE_L = "#eb6834", "#fff1e8"
VIOLET, VIOLET_L = "#4a3aa7", "#ecebf7"
GRAY_L = "#f3f2ed"

X0, X1, SEQ_MAX = 120, 1360, 1400
parts = []


def X(seq):
    return X0 + seq * (X1 - X0) / SEQ_MAX


def text(x, y, s, size, color, anchor="start", weight="400", family=None):
    fam = f' font-family="{family}"' if family else ''
    return (f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" '
            f'font-weight="{weight}" fill="{color}"{fam}>{s}</text>')


def seg(a, b, y, label, stroke, fill, dashed=False, tcolor=INK):
    dash = ' stroke-dasharray="6,4"' if dashed else ''
    parts.append(f'<rect x="{X(a)+1}" y="{y}" width="{X(b)-X(a)-2}" height="34" rx="6" fill="{fill}" stroke="{stroke}" stroke-width="1.5"{dash}/>')
    parts.append(text((X(a) + X(b)) / 2, y + 22, label, 12, tcolor, "middle", "700"))


parts.append(text(W / 2, 46, "TCP 重组：一个方向上的字节流", 26, INK, "middle", "700"))
parts.append(text(W / 2, 74, "段按序号放进红黑树(seg_tree)，数据拷进流式缓冲区(sb)；IDS 模式下，只有被对方 ACK 的部分才交给应用层", 14, SUB, "middle"))

# ---- 序号轴 ----
AX_Y = 116
parts.append(f'<line x1="{X0}" y1="{AX_Y}" x2="{X1}" y2="{AX_Y}" stroke="#c3c2b7" stroke-width="1.5"/>')
for s in range(0, SEQ_MAX + 1, 200):
    parts.append(f'<line x1="{X(s)}" y1="{AX_Y-4}" x2="{X(s)}" y2="{AX_Y+4}" stroke="#c3c2b7" stroke-width="1.5"/>')
    parts.append(text(X(s), AX_Y - 10, f"+{s}", 11, MUTED, "middle", family=MONO))
parts.append(text(40, AX_Y + 4, "序号", 12, SUB, weight="700"))

# ---- 第一行：段(到达顺序) ----
R1, R2 = 140, 182
parts.append(text(40, R1 + 22, "收到的段", 12, SUB, weight="700"))
parts.append(text(40, R1 + 42, "#号 = 到达顺序", 11, MUTED))
seg(0, 300, R1, "#1", BLUE, BLUE_L)
seg(300, 600, R1, "#3 乱序，后到", BLUE, BLUE_L)
seg(600, 900, R1, "#2", BLUE, BLUE_L)
seg(1200, 1400, R1, "#6", BLUE, BLUE_L)
seg(600, 900, R2, "#4 重传，数据相同：不重复存", "#c3c2b7", GRAY_L, dashed=True, tcolor=SUB)
seg(850, 1050, R2 + 42, "#5 与 #2 重叠", ORANGE, ORANGE_L, tcolor="#a8431c")

# ---- 第二行：流式缓冲区 ----
SB_Y = 290
parts.append(text(40, SB_Y + 22, "缓冲区 sb", 12, SUB, weight="700"))
parts.append(f'<rect x="{X(0)}" y="{SB_Y}" width="{X(1050)-X(0)}" height="34" rx="6" fill="#d5e5f8" stroke="{BLUE}" stroke-width="1.5"/>')
parts.append(f'<rect x="{X(1050)+2}" y="{SB_Y}" width="{X(1200)-X(1050)-4}" height="34" rx="6" fill="#fcfcfb" stroke="{MUTED}" stroke-width="1.5" stroke-dasharray="5,4"/>')
parts.append(text(X(1160), SB_Y + 22, "没抓到", 12, SUB, "middle", "700"))
parts.append(f'<rect x="{X(1200)}" y="{SB_Y}" width="{X(1400)-X(1200)}" height="34" rx="6" fill="#d5e5f8" stroke="{BLUE}" stroke-width="1.5"/>')
parts.append(text(X(300), SB_Y + 22, "按序号拼成连续的字节", 12, "#1f5fae", "middle", "700"))

# ---- 指针 ----
PT_Y = SB_Y + 34
for seqv, name, color in ((600, "app_progress：应用层读到这里", VIOLET), (1100, "last_ack：对方确认收到这里", ORANGE)):
    x = X(seqv)
    parts.append(f'<line x1="{x}" y1="{R1-6}" x2="{x}" y2="{PT_Y+26}" stroke="{color}" stroke-width="2" stroke-dasharray="3,3"/>')
    parts.append(f'<polygon points="{x-5},{PT_Y+26} {x+5},{PT_Y+26} {x},{PT_Y+18}" fill="{color}"/>')
    parts.append(text(x, PT_Y + 44, name, 12, "#4a3aa7" if color == VIOLET else "#a8431c", "middle", "700", MONO))

# ---- 区间说明 ----
BR_Y = PT_Y + 70


def brace(a, b, y, label, color, sub=None):
    xa, xb = X(a) + 2, X(b) - 2
    parts.append(f'<path d="M {xa} {y} L {xa} {y+8} L {xb} {y+8} L {xb} {y}" fill="none" stroke="{color}" stroke-width="1.6"/>')
    parts.append(text((xa + xb) / 2, y + 28, label, 12.5, INK, "middle", "700"))
    if sub:
        parts.append(text((xa + xb) / 2, y + 46, sub, 11.5, SUB, "middle"))


brace(0, 600, BR_Y, "已经交给应用层", MUTED)
brace(600, 1050, BR_Y, "被对方 ACK 了：交给应用层", VIOLET, "AppLayerHandleTCPData()")
brace(1200, 1400, BR_Y, "收到了，对方还没 ACK", BLUE, "先存着，等 ACK")
# 缺口：区间太窄，用引线
gx = (X(1050) + X(1100)) / 2
parts.append(f'<path d="M {X(1050)+2} {BR_Y} L {X(1050)+2} {BR_Y+8} L {X(1100)-2} {BR_Y+8} L {X(1100)-2} {BR_Y}" fill="none" stroke="#a8431c" stroke-width="1.6"/>')
parts.append(f'<line x1="{gx}" y1="{BR_Y+8}" x2="{gx}" y2="{BR_Y+64}" stroke="#a8431c" stroke-width="1.2"/>')
parts.append(text(gx, BR_Y + 80, "缺口：ACK 了却没抓到", 12.5, "#a8431c", "middle", "700"))
parts.append(text(gx, BR_Y + 98, "通知应用层 STREAM_GAP", 11.5, SUB, "middle"))

# ---- 底部三条说明 ----
CY = BR_Y + 130
notes = [
    ("乱序与重传", BLUE, ["段按序号插进红黑树，先后无所谓；", "数据按序号拷进缓冲区的对应位置。", "重传的段数据相同，不重复存。"]),
    ("重叠：同一段序号两份数据", ORANGE, ["数据不同时，按目标主机的操作系统策略", "决定用哪份(IDS)，或把包改回先到的那份(inline)；", "开启检查时记 overlap_different_data 事件。"]),
    ("为什么等 ACK", VIOLET, ["IDS 模式只交出接收端确认过的数据，", "没被接收的数据不会被当成真的；", "inline 模式要先判再转发，收到就处理。"]),
]
bw = (X1 - X0 - 40) / 3
for i, (title, color, lines) in enumerate(notes):
    bx = X0 + i * (bw + 20)
    parts.append(f'<rect x="{bx}" y="{CY}" width="{bw}" height="104" rx="10" fill="#fcfcfb" stroke="{color}" stroke-width="1.4"/>')
    tc = {BLUE: "#1f5fae", ORANGE: "#a8431c", VIOLET: "#4a3aa7"}[color]
    parts.append(text(bx + 14, CY + 26, title, 14, tc, weight="700"))
    for j, ln in enumerate(lines):
        parts.append(text(bx + 14, CY + 50 + j * 19, ln, 11.5, SUB))

H = CY + 104 + 34
head = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'font-family="-apple-system, \'Segoe UI\', \'PingFang SC\', \'Microsoft YaHei\', sans-serif">'
        f'<rect x="0" y="0" width="{W}" height="{H}" fill="#fcfcfb"/>')
with open(OUT, 'w', encoding='utf-8') as f:
    f.write(head + ''.join(parts) + '</svg>')
print('wrote', OUT, 'H =', H)
