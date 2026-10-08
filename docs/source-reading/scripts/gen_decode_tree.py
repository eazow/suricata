# -*- coding: utf-8 -*-
"""解码分发树：每一层看"下一层是什么"的字段，决定调用哪个解码函数；隧道和分片会生出新的 Packet。
函数名均对照 suricata-8.0.7 源码核实。"""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'images', 'suricata-decode-tree.svg')

W = 1480
INK, SUB, MUTED = "#0b0b0b", "#52514e", "#898781"
MONO = "'SF Mono', Menlo, Consolas, monospace"
STYLE = {  # 填充, 边框, 文字
    "path":   ("#2a78d6", "#2a78d6", "#ffffff"),   # 本文例子(curl 的 HTTP 包)走的路
    "other":  ("#f3f2ed", "#c3c2b7", SUB),
    "tunnel": ("#ecebf7", "#8a7fd0", "#4a3aa7"),
    "end":    ("#eb6834", "#eb6834", "#ffffff"),
}
COL_X = [40, 300, 560, 830, 1110]
COL_W = [220, 220, 230, 240, 330]
TOP, ROW_H, ROW_GAP = 150, 40, 12

parts = []
nodes = {}


def text(x, y, s, size, color, anchor="start", weight="400", family=None):
    fam = f' font-family="{family}"' if family else ''
    return (f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" '
            f'font-weight="{weight}" fill="{color}"{fam}>{s}</text>')


def node(key, col, row, label, style, sub=None, h=ROW_H):
    x = COL_X[col]
    y = TOP + row * (ROW_H + ROW_GAP)
    w = COL_W[col]
    fill, stroke, tcolor = STYLE[style]
    parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{fill}" stroke="{stroke}" stroke-width="1.3"/>')
    if sub:
        parts.append(text(x + 12, y + 17, label, 12.5, tcolor, weight="700", family=MONO))
        parts.append(text(x + 12, y + 33, sub, 10.5, tcolor))
    else:
        parts.append(text(x + 12, y + h / 2 + 4.5, label, 12.5, tcolor, weight="700", family=MONO))
    nodes[key] = (x, y, w, h)


def edge(a, b, color=None, dashed=False, label=None):
    ax, ay, aw, ah = nodes[a]
    bx, by, bw, bh = nodes[b]
    x1, y1 = ax + aw, ay + ah / 2
    x2, y2 = bx, by + bh / 2
    mx = x1 + 16
    c = color or "#b9b7ad"
    dash = ' stroke-dasharray="5,4"' if dashed else ''
    parts.append(f'<path d="M {x1} {y1} L {mx} {y1} L {mx} {y2} L {x2-7} {y2}" fill="none" stroke="{c}" stroke-width="1.6"{dash}/>')
    parts.append(f'<polygon points="{x2-7},{y2-4.5} {x2},{y2} {x2-7},{y2+4.5}" fill="{c}"/>')
    if label:
        parts.append(text(mx + 6, y2 - 6, label, 10.5, c))


parts.append(text(W / 2, 46, "解码分发树：一层层剥开，每一层决定下一层交给谁", 25, INK, "middle", "700"))
parts.append(text(W / 2, 74, "蓝色是开头 curl 那个 HTTP 包走的路；紫色是会生出新 Packet 的分支(隧道、分片)", 14, SUB, "middle"))

heads = ["入口：按 datalink", "链路层：按 eth_type", "网络层：按 ip proto", "传输层 / 隧道", "之后"]
for i, h in enumerate(heads):
    parts.append(text(COL_X[i], 124, h, 13, INK, weight="700"))

# 第 0 列
node("afp", 0, 0, "DecodeAFP()", "path")
node("ll", 0, 1, "DecodeLinkLayer()", "path", "switch (p->datalink)", h=ROW_H)
ax_, ay_, aw_, ah_ = nodes["afp"]
cx_ = ax_ + aw_ / 2
parts.append(f'<line x1="{cx_}" y1="{ay_+ah_}" x2="{cx_}" y2="{ay_+ah_+ROW_GAP-6}" stroke="#2a78d6" stroke-width="1.6"/>')
parts.append(f'<polygon points="{cx_-4.5},{ay_+ah_+ROW_GAP-6} {cx_+4.5},{ay_+ah_+ROW_GAP-6} {cx_},{ay_+ah_+ROW_GAP}" fill="#2a78d6"/>')
# 第 1 列
node("eth", 1, 1, "DecodeEthernet()", "path")
node("sll", 1, 2, "DecodeSll() 等", "other", "Linux cooked / PPP / Raw …")
edge("ll", "eth", "#2a78d6")
edge("ll", "sll")
# 第 2 列
l2 = [("vlan", "DecodeVLAN()", "other", "剥掉标签，再回到这一层"),
      ("mpls", "DecodeMPLS()", "other", None),
      ("pppoe", "DecodePPPOESession()", "other", None),
      ("arp", "DecodeARP()", "other", None),
      ("ipv4", "DecodeIPV4()", "path", None),
      ("ipv6", "DecodeIPV6()", "other", None)]
for i, (k, lbl, st, sub) in enumerate(l2):
    node(k, 2, i, lbl, st, sub)
    edge("eth", k, "#2a78d6" if st == "path" else None)
# 第 3 列
l3 = [("tcp", "DecodeTCP()", "path", None),
      ("udp", "DecodeUDP()", "other", "按端口认 VXLAN / Geneve / Teredo"),
      ("icmp", "DecodeICMPV4()", "other", None),
      ("sctp", "DecodeSCTP() / DecodeESP()", "other", None),
      ("gre", "DecodeGRE()", "tunnel", "GRE 隧道"),
      ("ipip", "IPIP / IPv6-in-IPv4", "tunnel", "ip proto 4 / 41"),
      ("frag", "Defrag()", "tunnel", "分片(MF 或 offset>0)：先攒齐再重组")]
for i, (k, lbl, st, sub) in enumerate(l3):
    node(k, 3, i, lbl, st, sub)
    c = "#2a78d6" if st == "path" else ("#8a7fd0" if st == "tunnel" else None)
    edge("ipv4", k, c)
# 第 4 列
node("flow", 4, 0, "FlowSetupPacket()", "end", "打上 PKT_WANTS_FLOW，算好 flow_hash → 第 5 篇")
edge("tcp", "flow", "#eb6834")
node("tun", 4, 4, "PacketTunnelPktSetup()", "tunnel", "新 Packet 拷贝内层数据，root 指向外层")
node("rebuilt", 4, 6, "PacketDefragPktSetup()", "tunnel", "拼好的新 Packet，再调 DecodeIPV4()")
edge("udp", "tun", "#8a7fd0", dashed=True)
edge("gre", "tun", "#8a7fd0")
edge("ipip", "tun", "#8a7fd0")
edge("frag", "rebuilt", "#8a7fd0")
node("pq", 4, 5, "tv->decode_pq", "tunnel", "新 Packet 排在这里，解码完再走后面的工位")
# 新包 → decode_pq 的竖向箭头
tx, ty, tw, th = nodes["tun"]
qx, qy, qw, qh = nodes["pq"]
rx, ry, rw, rh = nodes["rebuilt"]
for yy_from, yy_to in ((ty + th, qy), (ry, qy + qh)):
    cx = tx + tw / 2
    d = 1 if yy_to > yy_from else -1
    parts.append(f'<line x1="{cx}" y1="{yy_from}" x2="{cx}" y2="{yy_to - 7*d}" stroke="#8a7fd0" stroke-width="1.6"/>')
    parts.append(f'<polygon points="{cx-4.5},{yy_to-7*d} {cx+4.5},{yy_to-7*d} {cx},{yy_to}" fill="#8a7fd0"/>')

# 底部：每一层的固定套路
by = TOP + 7 * (ROW_H + ROW_GAP) + 24
parts.append(f'<rect x="40" y="{by}" width="{W-80}" height="92" rx="12" fill="#fcfcfb" stroke="#dcdad2" stroke-width="1.2"/>')
parts.append(text(60, by + 28, "每一层的固定套路", 14, INK, weight="700"))
parts.append(text(60, by + 56, "① 长度够不够  →  ② PacketIncreaseCheckLayers()：层数不超过 max-layers(默认 16)  →  ③ PacketSetXxx()：把头部指针记进 p->l2 / l3 / l4  →  ④ 按类型字段调用下一层", 12, SUB))
parts.append(text(60, by + 78, "任何一步不过：ENGINE_SET_INVALID_EVENT() 记一个解码事件，提前返回；包不会进流表，但仍会经过检测和输出。", 12, "#c24e1f"))

H = by + 92 + 30
head = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'font-family="-apple-system, \'Segoe UI\', \'PingFang SC\', \'Microsoft YaHei\', sans-serif">'
        f'<rect x="0" y="0" width="{W}" height="{H}" fill="#fcfcfb"/>')
with open(OUT, 'w', encoding='utf-8') as f:
    f.write(head + ''.join(parts) + '</svg>')
print('wrote', OUT, 'H =', H)
