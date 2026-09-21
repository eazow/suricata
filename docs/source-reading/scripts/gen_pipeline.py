# -*- coding: utf-8 -*-
import os
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'images')

W, H = 1560, 330
box_w, box_h = 174, 100
gap = 22
start_x = 40
top_y = 150

stages = [
    ("捕获", "AF_PACKET / PCAP / NFQ", "#6da7ec", "#0b0b0b", "第3篇"),
    ("解码", "Ether / IP / TCP", "#5598e7", "#0b0b0b", "第4篇"),
    ("Flow", "查找 / 建立", "#3987e5", "#ffffff", "第5篇"),
    ("Stream", "TCP 重组", "#2a78d6", "#ffffff", "第6篇"),
    ("应用层解析", "HTTP / TLS ...", "#256abf", "#ffffff", "第7篇"),
    ("规则检测", "MPM + SGH", "#1c5cab", "#ffffff", "第8-9篇"),
    ("输出", "EVE JSON", "#184f95", "#ffffff", "第10篇"),
]

source_w = 120

parts = []
parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="-apple-system, \'Segoe UI\', \'PingFang SC\', \'Microsoft YaHei\', sans-serif">')

# background
parts.append(f'<rect x="0" y="0" width="{W}" height="{H}" fill="#fcfcfb" rx="0"/>')
parts.append("""<filter id="softshadow" x="-20%" y="-20%" width="140%" height="140%"><feDropShadow dx="0" dy="3" stdDeviation="4" flood-color="#0b0b0b" flood-opacity="0.18"/></filter>""")

# title
parts.append(f'<text x="{W/2}" y="52" text-anchor="middle" font-size="28" font-weight="700" fill="#0b0b0b">Suricata 数据包流水线总览</text>')
parts.append(f'<text x="{W/2}" y="82" text-anchor="middle" font-size="15" fill="#52514e">一个包从网卡钻进来，依次经过这几道工位，最后变成一条 EVE JSON 告警</text>')

def rounded_box(x, y, w, h, fill, text_top, text_bottom, text_color, radius=14):
    s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" stroke="rgba(11,11,11,0.08)" stroke-width="1" filter="url(#softshadow)"/>'
    s += f'<text x="{x+w/2}" y="{y+h/2-6}" text-anchor="middle" font-size="19" font-weight="700" fill="{text_color}">{text_top}</text>'
    s += f'<text x="{x+w/2}" y="{y+h/2+18}" text-anchor="middle" font-size="11.5" fill="{text_color}" opacity="1">{text_bottom}</text>'
    return s

def arrow(x1, y, x2, color="#898781"):
    s = f'<line x1="{x1}" y1="{y}" x2="{x2-8}" y2="{y}" stroke="{color}" stroke-width="2.5"/>'
    s += f'<polygon points="{x2-8},{y-6} {x2},{y} {x2-8},{y+6}" fill="{color}"/>'
    return s

# source box
sx, sy = start_x, top_y
parts.append(rounded_box(sx, sy, source_w, box_h, "#e1e0d9", "网卡", "PCAP 文件", "#0b0b0b"))

x = sx + source_w
mid_y = top_y + box_h/2
parts.append(arrow(x, mid_y, x+gap))
x += gap

for i, (title, sub, color, tcolor, ep) in enumerate(stages):
    parts.append(rounded_box(x, top_y, box_w, box_h, color, title, sub, tcolor))
    # episode tag
    parts.append(f'<text x="{x+box_w/2}" y="{top_y+box_h+22}" text-anchor="middle" font-size="12" fill="#898781">{ep}</text>')
    x += box_w
    if i != len(stages)-1:
        parts.append(arrow(x, mid_y, x+gap))
    x += gap

parts.append('</svg>')

with open(os.path.join(OUT_DIR, 'suricata-pipeline.svg'), 'w', encoding='utf-8') as f:
    f.write(''.join(parts))

print("box end x:", x)
