# -*- coding: utf-8 -*-
import os
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'images')

W = 1200

BLUE = "#2a78d6"
BLUE_L = "#6da7ec"
VIOLET = "#4a3aa7"
ORANGE = "#eb6834"
GRAY = "#e1e0d9"
GRAY_D = "#898781"
INK = "#0b0b0b"
SUB = "#52514e"

def box(x, y, w, h, fill, title, sub=None, tcolor=INK, radius=10, stroke=None, fs_title=14.5, fs_sub=11, shadow=True):
    st = f' stroke="{stroke}" stroke-width="1.5"' if stroke else ' stroke="rgba(11,11,11,0.08)" stroke-width="1"'
    filt = ' filter="url(#softshadow)"' if shadow else ''
    s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}"{st}{filt}/>'
    if sub:
        s += f'<text x="{x+w/2}" y="{y+h/2-3}" text-anchor="middle" font-size="{fs_title}" font-weight="700" fill="{tcolor}">{title}</text>'
        s += f'<text x="{x+w/2}" y="{y+h/2+15}" text-anchor="middle" font-size="{fs_sub}" fill="{tcolor}">{sub}</text>'
    else:
        s += f'<text x="{x+w/2}" y="{y+h/2+5}" text-anchor="middle" font-size="{fs_title}" font-weight="700" fill="{tcolor}">{title}</text>'
    return s

def text(x, y, s, size=12.5, color=SUB, anchor="start", weight="400", style="normal"):
    return f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" fill="{color}" font-weight="{weight}" font-style="{style}">{s}</text>'

def lifeline(x, y1, y2, color="#c3c2b7", dashed=True):
    dash = ' stroke-dasharray="5,5"' if dashed else ''
    return f'<line x1="{x}" y1="{y1}" x2="{x}" y2="{y2}" stroke="{color}" stroke-width="1.8"{dash}/>'

def hline(x1, x2, y, color, label=None, label_dy=-8, dashed=False, label_anchor="middle"):
    dash = ' stroke-dasharray="5,4"' if dashed else ''
    s = f'<line x1="{x1}" y1="{y}" x2="{x2-8 if x2>x1 else x2+8}" y2="{y}" stroke="{color}" stroke-width="2"{dash}/>'
    end = x2-8 if x2 > x1 else x2+8
    if x2 > x1:
        s += f'<polygon points="{end},{y-5} {x2},{y} {end},{y+5}" fill="{color}"/>'
    else:
        s += f'<polygon points="{end},{y-5} {x2},{y} {end},{y+5}" fill="{color}"/>'
    if label:
        lx = (x1+x2)/2
        s += text(lx, y+label_dy, label, 11.5, color, "middle", "700" if not dashed else "400")
    return s

def actbar(x, y, h, w, color, label=None, label_color="#ffffff"):
    s = f'<rect x="{x-w/2}" y="{y}" width="{w}" height="{h}" rx="6" fill="{color}"/>'
    if label:
        # vertical-ish centered label, wrap manually by caller via \n handling omitted; put single line centered
        s += text(x, y+h/2+4, label, 11.5, label_color, "middle", "700")
    return s

parts = []
parts.append('<filter id="softshadow" x="-30%" y="-30%" width="160%" height="160%"><feDropShadow dx="0" dy="3" stdDeviation="4" flood-color="#0b0b0b" flood-opacity="0.16"/></filter>')

lane_x = {"main": 180, "worker": 620, "mgmt": 1020}
lane_w = 44

top = 100
parts.append(text(W/2, 40, "启动过程中：谁在什么时候被谁拉起来", 24, INK, "middle", "700"))
parts.append(text(W/2, 66, "主线程 / 抓包+检测工作线程 / 管理线程，三条时间线", 14, SUB, "middle"))

header_w, header_h = 260, 56
headers = [
    ("main", "主线程", "main() 一路跑下来的那条线"),
    ("worker", "工作线程组", "Receive→Decode→FlowWorker→…"),
    ("mgmt", "管理线程组", "FlowManager / Stats / LogFlush"),
]
hcolor = {"main": GRAY, "worker": BLUE, "mgmt": VIOLET}
htcolor = {"main": INK, "worker": "#ffffff", "mgmt": "#ffffff"}
for key, title, sub in headers:
    x = lane_x[key]
    parts.append(box(x-header_w/2, top, header_w, header_h, hcolor[key], title, sub, htcolor[key], fs_title=15, fs_sub=10.5))

bottom_of_header = top + header_h
y = bottom_of_header + 30

# Phase 1: main runs alone (pre-init through SuricataInit early steps)
phase1_h = 70
parts.append(lifeline(lane_x["main"], bottom_of_header, y+phase1_h+400))  # draw full main lifeline later trimmed visually is fine since bars cover it
parts.append(actbar(lane_x["main"], y, phase1_h, 34, GRAY_D))
parts.append(text(lane_x["main"]+30, y+18, "PreInit → ParseCommandLine → LoadYamlConfig", 12, SUB))
parts.append(text(lane_x["main"]+30, y+36, "→ SuricataInit() 前 7 步（单线程）", 12, SUB))

y_spawn = y + phase1_h + 46

# spawn arrows
parts.append(hline(lane_x["main"], lane_x["worker"], y_spawn, BLUE, "RunModeDispatch() 里 TmThreadSpawn()"))
parts.append(hline(lane_x["main"], lane_x["mgmt"], y_spawn+40, VIOLET, "FlowManagerThreadSpawn() 等"))

parts.append(lifeline(lane_x["worker"], y_spawn-10, y_spawn+400, BLUE_L))
parts.append(lifeline(lane_x["mgmt"], y_spawn+30, y_spawn+400, "#9085e9"))

y_ready = y_spawn + 40 + 50
# worker/mgmt report init done back to main
parts.append(hline(lane_x["worker"], lane_x["main"]+20, y_ready, GRAY_D, "THV_INIT_DONE", dashed=True))
parts.append(hline(lane_x["mgmt"], lane_x["main"]+20, y_ready+26, GRAY_D, "THV_INIT_DONE", dashed=True))

y_postinit = y_ready + 26 + 34
postinit_h = 44
parts.append(actbar(lane_x["main"], y_postinit, postinit_h, 34, GRAY_D))
parts.append(text(lane_x["main"]+30, y_postinit+26, "SuricataPostInit() — 等所有线程 init 完成，再放行", 12, SUB))

y_parallel = y_postinit + postinit_h + 30
parallel_h = 170

bar_w = 190
parts.append(f'<rect x="{lane_x["main"]-bar_w/2}" y="{y_parallel}" width="{bar_w}" height="{parallel_h}" rx="10" fill="{ORANGE}"/>')
parts.append(text(lane_x["main"], y_parallel+parallel_h/2-6, "SuricataMainLoop()", 13, "#ffffff", "middle", "700"))
parts.append(text(lane_x["main"], y_parallel+parallel_h/2+14, "信号响应 + 健康检查", 11.5, "#ffffff", "middle"))

parts.append(f'<rect x="{lane_x["worker"]-bar_w/2}" y="{y_parallel}" width="{bar_w}" height="{parallel_h}" rx="10" fill="{BLUE}"/>')
parts.append(text(lane_x["worker"], y_parallel+parallel_h/2-6, "抓包 → 解码 → 检测 → 输出", 13, "#ffffff", "middle", "700"))
parts.append(text(lane_x["worker"], y_parallel+parallel_h/2+14, "各自循环，互不等待", 11.5, "#ffffff", "middle"))

parts.append(f'<rect x="{lane_x["mgmt"]-bar_w/2}" y="{y_parallel}" width="{bar_w}" height="{parallel_h}" rx="10" fill="{VIOLET}"/>')
parts.append(text(lane_x["mgmt"], y_parallel+parallel_h/2-6, "flow 超时清理", 13, "#ffffff", "middle", "700"))
parts.append(text(lane_x["mgmt"], y_parallel+parallel_h/2+14, "统计 / 日志刷盘", 11.5, "#ffffff", "middle"))

parts.append(text(W/2, y_parallel+parallel_h+24, "三条线并发跑，谁也不等谁", 13, GRAY_D, "middle", "400", "italic"))

y_stop = y_parallel + parallel_h + 60
parts.append(hline(lane_x["main"]-60, lane_x["main"], y_stop, GRAY_D, None))
parts.append(text(lane_x["main"]-70, y_stop+4, "SIGINT / SIGTERM", 11.5, SUB, "end"))

y_kill = y_stop + 36
parts.append(hline(lane_x["main"], lane_x["worker"], y_kill, GRAY_D, "TmThreadKillThreads() / THV_KILL", dashed=True))
parts.append(hline(lane_x["main"], lane_x["mgmt"], y_kill+30, GRAY_D, "THV_KILL", dashed=True))

y_end = y_kill + 30 + 46
end_w, end_h = 300, 52
parts.append(box(lane_x["main"]-end_w/2, y_end, end_w, end_h, GRAY, "SuricataShutdown() → GlobalsDestroy()", None, INK, fs_title=12.5))

H = int(y_end + end_h + 30)

svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="-apple-system, \'Segoe UI\', \'PingFang SC\', \'Microsoft YaHei\', sans-serif">']
svg.append(f'<rect x="0" y="0" width="{W}" height="{H}" fill="#fcfcfb"/>')
svg.extend(parts)
svg.append('</svg>')

with open(os.path.join(OUT_DIR, 'suricata-startup-sequence.svg'), 'w', encoding='utf-8') as f:
    f.write(''.join(svg))
print("H=", H)
