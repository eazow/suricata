# -*- coding: utf-8 -*-
"""从规则命中到一行 JSON：告警先进队列、包检测完统一收尾；OutputLoggerLog() 分发给几类根日志器，
各日志模块按条件或事务进度写日志；EVE 用 JsonBuilder 拼出一行 JSON，写到文件、syslog、unix socket 或 redis。
函数名与默认值均对照 suricata-8.0.7 源码核实。"""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'images', 'suricata-output.svg')

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
    s = s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    return (f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" '
            f'font-weight="{weight}" fill="{color}"{fam}>{s}</text>')


def box(x, y, w, h, title, lines, stroke, fill, tcolor, mono_title=False, dashed=False):
    dash = ' stroke-dasharray="6,4"' if dashed else ''
    parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{fill}" stroke="{stroke}" stroke-width="1.5"{dash}/>')
    parts.append(text(x + 14, y + 25, title, 14, tcolor, weight="700", family=MONO if mono_title else None))
    for i, ln in enumerate(lines):
        parts.append(text(x + 14, y + 47 + i * 19, ln, 11.5, SUB))
    return x, y, w, h


def harrow(x1, x2, y, color):
    parts.append(f'<line x1="{x1}" y1="{y}" x2="{x2-8}" y2="{y}" stroke="{color}" stroke-width="1.8"/>')
    parts.append(f'<polygon points="{x2-8},{y-5} {x2-8},{y+5} {x2},{y}" fill="{color}"/>')


def varrow(x, y1, y2, color, dashed=False):
    dash = ' stroke-dasharray="6,4"' if dashed else ''
    parts.append(f'<line x1="{x}" y1="{y1}" x2="{x}" y2="{y2-8}" stroke="{color}" stroke-width="1.8"{dash}/>')
    parts.append(f'<polygon points="{x-5},{y2-8} {x+5},{y2-8} {x},{y2}" fill="{color}"/>')


parts.append(text(W / 2, 46, "从规则命中到一行 JSON", 26, INK, "middle", "700"))
parts.append(text(W / 2, 74, "告警先攒进队列再统一收尾；日志按类型分发，各模块按条件或事务进度写出；EVE 拼成一行 JSON 写出去", 14, SUB, "middle"))

# ---- 第一行：告警 ----
R1 = 104
a1 = box(40, R1, 300, 118, "规则命中", ["AlertQueueAppend()：", "先放进本线程的告警队列，", "不立即生效"], ROSE, ROSE_L, ROSE_T)
a2 = box(400, R1, 520, 118, "包检测完：PacketAlertFinalize()", ["按规则顺序排序 → 逐条做抑制、阈值检查 →", "执行 drop、pass 这类动作 →", "写进 p->alerts，每个包最多 15 条(packet-alert-max)，", "被抑制的、超出上限的只计数"], ROSE, ROSE_L, ROSE_T)
a3 = box(980, R1, 460, 118, "FlowWorker 最后一步：OutputLoggerLog()", ["对每个包都调用(第 5 篇)，", "依次调用几类根日志器"], BLUE, BLUE_L, BLUE_T)
harrow(340, 400, R1 + 59, ROSE)
harrow(920, 980, R1 + 59, GRAY)

# ---- 第二行：根日志器 ----
R2 = R1 + 196
parts.append(text(40, R2 - 44, "几类根日志器(OutputRegisterRootLoggers())，各自管一批日志模块", 14, INK, weight="700"))
roots = [
    ("包", "OutputPacketLog()", ["每个模块带一个条件函数", "alert：p->alerts.cnt > 0 才写", "另有 drop、anomaly 等"], ROSE, ROSE_L, ROSE_T),
    ("事务", "OutputTxLog()", ["逐个事务、逐个模块判断：", "事务进度够了才写，写完打标记", "http：两个方向都完成才写"], VIOLET, VIOLET_L, VIOLET),
    ("文件 / 文件数据 / 流式", "", ["fileinfo、filestore、", "按流写原始数据等"], GRAY, GRAY_L, INK),
]
rw, rg = 450, 25
for i, (t, fn, ls, st, fl, tc) in enumerate(roots):
    rx = 40 + i * (rw + rg)
    parts.append(f'<rect x="{rx}" y="{R2}" width="{rw}" height="118" rx="10" fill="{fl}" stroke="{st}" stroke-width="1.5"/>')
    parts.append(text(rx + 14, R2 + 25, t, 14, tc, weight="700"))
    if fn:
        parts.append(text(rx + 14 + len(t) * 15 + 12, R2 + 25, fn, 12, MUTED, family=MONO))
    for j, ln in enumerate(ls):
        parts.append(text(rx + 14, R2 + 50 + j * 20, ln, 11.5, SUB))
bus_y = R2 - 22
parts.append(f'<line x1="{a3[0] + 60}" y1="{R1 + 118}" x2="{a3[0] + 60}" y2="{bus_y}" stroke="{GRAY}" stroke-width="1.8"/>')
parts.append(f'<line x1="{40 + rw / 2}" y1="{bus_y}" x2="{40 + 2 * (rw + rg) + rw / 2}" y2="{bus_y}" stroke="{GRAY}" stroke-width="1.8"/>')
for i in range(3):
    varrow(40 + i * (rw + rg) + rw / 2, bus_y, R2, GRAY)

side_y = R2 + 136

# ---- 第三行：EVE 拼 JSON ----
R3 = side_y + 20
j1 = box(40, R3, 450, 128, "拼 JSON：JsonBuilder(Rust 实现)", ["CreateEveHeader()：所有事件共用的头", "timestamp、flow_id、event_type、", "五元组、pkt_src、tx_id …", "再加各模块自己的字段"], ORANGE, ORANGE_L, ORANGE_T)
j2 = box(550, R3, 430, 128, "alert 事件多了什么", ["\"alert\"：action、signature_id、rev、", "signature、category、severity …", "可选：命中事务的应用层字段(如 http)、", "payload、flow 信息"], ORANGE, ORANGE_L, ORANGE_T)
j3 = box(1040, R3, 400, 128, "写出去：OutputJsonBuilderBuffer()", ["拼好的一行放进本线程的缓冲区，", "LogFileWrite() 写到 eve.json；", "filetype 也可以是 syslog、", "unix socket 或 redis"], ORANGE, ORANGE_L, ORANGE_T)
harrow(490, 550, R3 + 64, ORANGE)
harrow(980, 1040, R3 + 64, ORANGE)
varrow(40 + 225, R2 + 118, R3, ROSE)
varrow(40 + rw + rg + 225, R2 + 118, R3, VIOLET)

parts.append(text(40, R3 + 128 + 32, "不走这条路的：flow 日志在流被回收时由 FlowRecycler 调 OutputFlowLog() 写出(第 5 篇)；stats 日志由专门的统计线程定时写出。", 12, SUB))
H = R3 + 128 + 56
head = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'font-family="-apple-system, \'Segoe UI\', \'PingFang SC\', \'Microsoft YaHei\', sans-serif">'
        f'<rect x="0" y="0" width="{W}" height="{H}" fill="#fcfcfb"/>')
with open(OUT, 'w', encoding='utf-8') as f:
    f.write(head + ''.join(parts) + '</svg>')
print('wrote', OUT, 'H =', H)
