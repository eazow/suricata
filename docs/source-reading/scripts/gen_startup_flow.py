# -*- coding: utf-8 -*-
import os
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'images')

W = 900

GRAY = "#e1e0d9"
GRAY_D = "#898781"
BLUE = "#2a78d6"
BLUE_L = "#6da7ec"
VIOLET = "#4a3aa7"
ORANGE = "#eb6834"
INK = "#0b0b0b"
SUB = "#52514e"

parts = []
defs = []
defs.append('<filter id="softshadow" x="-30%" y="-30%" width="160%" height="160%"><feDropShadow dx="0" dy="3" stdDeviation="4" flood-color="#0b0b0b" flood-opacity="0.16"/></filter>')

def box(x, y, w, h, fill, title, sub=None, tcolor=INK, radius=12, stroke=None, dashed=False, fs_title=15.5, fs_sub=11.5):
    dash = ' stroke-dasharray="6,4"' if dashed else ''
    st = f' stroke="{stroke}" stroke-width="1.5"' if stroke else ' stroke="rgba(11,11,11,0.08)" stroke-width="1"'
    s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}"{st}{dash} filter="url(#softshadow)"/>'
    if sub:
        s += f'<text x="{x+w/2}" y="{y+h/2-3}" text-anchor="middle" font-size="{fs_title}" font-weight="700" fill="{tcolor}">{title}</text>'
        s += f'<text x="{x+w/2}" y="{y+h/2+16}" text-anchor="middle" font-size="{fs_sub}" fill="{tcolor}">{sub}</text>'
    else:
        s += f'<text x="{x+w/2}" y="{y+h/2+5}" text-anchor="middle" font-size="{fs_title}" font-weight="700" fill="{tcolor}">{title}</text>'
    return s

def plain_box(x, y, w, h, fill, radius=10, stroke=None, dashed=False):
    dash = ' stroke-dasharray="6,4"' if dashed else ''
    st = f' stroke="{stroke}" stroke-width="1.5"' if stroke else ' stroke="rgba(11,11,11,0.08)" stroke-width="1"'
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}"{st}{dash}/>'

def text(x, y, s, size=13, color=SUB, anchor="start", weight="400"):
    return f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" fill="{color}" font-weight="{weight}">{s}</text>'

def varrow(x, y1, y2, color=GRAY_D):
    s = f'<line x1="{x}" y1="{y1}" x2="{x}" y2="{y2-8}" stroke="{color}" stroke-width="2.2"/>'
    s += f'<polygon points="{x-6},{y2-8} {x+6},{y2-8} {x},{y2}" fill="{color}"/>'
    return s

y = 60
cx = W/2

body = []

# title
body.append(text(cx, 40, "main() 启动流程", 26, INK, "middle", "700"))

y = 68
# main() pill
pill_w, pill_h = 200, 56
body.append(box(cx-pill_w/2, y, pill_w, pill_h, GRAY, "main()", None, INK))
y2 = y + pill_h
y += pill_h + 34
body.append(varrow(cx, y2, y))

# early steps row: 3 boxes
row_w, row_h = 250, 56
gap = 30
total = row_w*3 + gap*2
sx = cx - total/2
labels = [("SuricataPreInit()", "早期初始化"), ("SCParseCommandLine()", "argv → SCInstance"), ("SCLoadYamlConfig()", "加载 suricata.yaml")]
for i, (t, s) in enumerate(labels):
    bx = sx + i*(row_w+gap)
    body.append(box(bx, y, row_w, row_h, BLUE_L, t, s, INK, fs_title=14))
y2 = y + row_h
y += row_h + 34
body.append(varrow(cx, y2, y))

# SuricataInit container
init_w = 760
init_x = cx - init_w/2
init_steps = [
    "1. GlobalsInitPreConfig() — 时间、阈值、协议名表",
    "2. 读取 yaml 配置项，配置日志系统 SCLogLoadConfig",
    "3. RunModeInitializeThreadSettings() — 线程数/亲和性",
    "4. ParseInterfacesList() — 监听哪些网卡/pcap",
    "5. PostConfLoadedSetup() — 注册模块、各子系统初始化",
    "6. SCDropMainThreadCaps() — 权限收敛",
    "7. PostConfLoadedDetectSetup() — 建检测引擎、加载规则",
]
step_h = 27
init_inner_top = 46
init_h = init_inner_top + step_h*len(init_steps) + 70
body.append(plain_box(init_x, y, init_w, init_h, "#fcfcfb", radius=16, stroke="#c3c2b7", dashed=True))
body.append(text(init_x+22, y+28, "SuricataInit()  —— 真正的初始化重头戏", 16, INK, weight="700"))
sy = y + init_inner_top
for step in init_steps:
    body.append(text(init_x+34, sy+18, step, 12.5, SUB))
    sy += step_h

# RunModeDispatch highlighted sub-box inside SuricataInit container
rd_w, rd_h = init_w-64, 60
rd_x = init_x+32
rd_y = sy + 6
body.append(box(rd_x, rd_y, rd_w, rd_h, VIOLET, "8. RunModeDispatch()  —— 流水线在这一刻被焊起来", None, "#ffffff", fs_title=14))

y2 = y + init_h
y += init_h + 34
body.append(varrow(cx, y2, y))

# RunModeDispatch detail box
rdd_w = 760
rdd_x = cx - rdd_w/2
rdd_items = [
    ("mode->RunModeFunc()", "组装 TmModule 流水线，创建工作线程"),
    ("FlowManagerThreadSpawn() 等", "拉起 Flow 管理、统计、日志刷盘等线程"),
    ("TmThreadsSealThreads()", "封口：之后不再允许创建新线程"),
]
item_w = (rdd_w - 2*40) / 3
rdd_h = 110
body.append(plain_box(rdd_x, y, rdd_w, rdd_h, "#f3f0fb", radius=16, stroke=VIOLET))
body.append(text(rdd_x+24, y+26, "RunModeDispatch() 内部", 14, VIOLET, weight="700"))
ix = rdd_x + 30
iw = (rdd_w - 60 - 2*24) / 3
for i, (t, s) in enumerate(rdd_items):
    body.append(box(ix, y+38, iw, 58, VIOLET, t, s, "#ffffff", fs_title=12.5, fs_sub=10.5))
    ix += iw + 24

y2 = y + rdd_h
y += rdd_h + 34
body.append(varrow(cx, y2, y))

# PostInit
pi_w, pi_h = 420, 56
body.append(box(cx-pi_w/2, y, pi_w, pi_h, BLUE_L, "SuricataPostInit()", "等所有线程 init 完成，再统一放行", INK, fs_title=14))
y2 = y+pi_h
y += pi_h + 34
body.append(varrow(cx, y2, y))

# MainLoop
ml_w, ml_h = 460, 66
body.append(box(cx-ml_w/2, y, ml_w, ml_h, ORANGE, "SuricataMainLoop()", "主线程真正待着的地方：信号响应 + 健康检查", "#ffffff", fs_title=15))
y2 = y+ml_h
y += ml_h + 34
body.append(varrow(cx, y2, y))

# Shutdown
sd_w, sd_h = 420, 56
body.append(box(cx-sd_w/2, y, sd_w, sd_h, GRAY, "SuricataShutdown() → GlobalsDestroy()", "杀线程、收尾、进程退出", INK, fs_title=13))
y += sd_h + 40

H = int(y)

svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="-apple-system, \'Segoe UI\', \'PingFang SC\', \'Microsoft YaHei\', sans-serif">']
svg.extend(defs)
svg.append(f'<rect x="0" y="0" width="{W}" height="{H}" fill="#fcfcfb"/>')
svg.extend(body)
svg.append('</svg>')

with open(os.path.join(OUT_DIR, 'suricata-startup-flow.svg'), 'w', encoding='utf-8') as f:
    f.write(''.join(svg))
print("H=", H)
