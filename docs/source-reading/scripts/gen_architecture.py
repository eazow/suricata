# -*- coding: utf-8 -*-
"""Suricata 分层架构图：控制面 | 数据面(Worker 线程流水线) | 管理线程与共享状态 + 底层基础设施。
所有函数名、文件名均对照 v8.0.7 源码核实。"""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'images', 'suricata-architecture.svg')

W = 1880
INK, SUB, MUTED = "#15151a", "#4d4c48", "#8a8983"
PAGE, SURFACE, LINE = "#f3f2ed", "#ffffff", "#dcdad2"
MONO = "'SFMono-Regular','JetBrains Mono','Menlo','Consolas',monospace"
C = {
    "src": "#5b6472", "cap": "#2a78d6", "dec": "#e0662f", "flow": "#13a06e",
    "stream": "#0f8a8a", "app": "#c08000", "det": "#c2407a", "out": "#2f8f2f",
    "ips": "#b83232", "ctl": "#4a3aa7", "mgmt": "#6b4fb8", "base": "#3d4a5c",
}


def tint(h, r=0.12):
    h = h.lstrip('#')
    rgb = [int(h[i:i + 2], 16) for i in (0, 2, 4)]
    return "#" + "".join(f"{int(c * r + 255 * (1 - r)):02x}" for c in rgb)


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def tw(s, size):
    """粗略估算文本宽度：CJK 约 1 个字号宽，ASCII 约 0.6 个字号宽。"""
    return sum(size if ord(ch) > 127 else size * 0.6 for ch in s)


o = []


def rect(x, y, w, h, fill, stroke="none", sw=1, r=12, dash=None, shadow=False):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    f = ' filter="url(#sh)"' if shadow else ''
    o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" '
             f'stroke="{stroke}" stroke-width="{sw}"{d}{f}/>')


def text(x, y, s, size=13, color=SUB, anchor="start", weight=400, mono=False):
    fam = f' font-family="{MONO}"' if mono else ''
    o.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" text-anchor="{anchor}" '
             f'font-weight="{weight}"{fam}>{esc(s)}</text>')


def arrow(x1, y1, x2, y2, color=MUTED, sw=2, dash=None, marker="ah"):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    o.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{sw}"{d} '
             f'marker-end="url(#{marker})"/>')


def path(dstr, color=MUTED, sw=2, dash=None, marker="ah"):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    o.append(f'<path d="{dstr}" fill="none" stroke="{color}" stroke-width="{sw}"{d} marker-end="url(#{marker})"/>')


def chip(x, y, label, color, size=11.5, h=24, mono=True, filled=False):
    w = tw(label, size) + 20
    rect(x, y, w, h, color if filled else tint(color, 0.10), stroke="none" if filled else tint(color, 0.35), r=h / 2)
    text(x + w / 2, y + h / 2 + size * 0.36, label, size, "#fff" if filled else color, "middle", 700, mono)
    return w


def chips(x, y, labels, color, gap=8, size=11.5, max_x=None):
    cx = x
    for lb in labels:
        if max_x and cx + tw(lb, size) + 20 > max_x:
            cx, y = x, y + 32
        cx += chip(cx, y, lb, color, size) + gap
    return y + 24


def badge(x, y, num, color):
    rect(x, y, 30, 30, color, r=8)
    text(x + 15, y + 20, num, 13, "#fff", "middle", 800, True)


# ------------------------------------------------------------------ 画布参数
M = 32
LX, LW = M, 300                      # 左：启动与控制平面
CX = LX + LW + 26                    # 中：数据平面
RW = 300
RX = W - M - RW                      # 右：管理线程与共享状态
CW = RX - 26 - CX
STRIP = 168                          # 数据平面每层左侧标签条宽度

# ------------------------------------------------------------------ 标题
text(M, 50, "Suricata 架构总览", 30, INK, weight=800)
text(M + 262, 50, "Layered Architecture · v8.0.7", 15, MUTED, weight=600, mono=True)
text(M, 78, "一个包从网卡进来，在 Worker 线程里依次经过 采集 → 解码 → FlowWorker(流 / 重组 / 应用层 / 检测 / 输出) → 裁决；"
            "左侧控制平面负责把这条流水线搭起来，右侧管理线程在后台维护共享状态。", 13.5, SUB)
leg = [("数据流(包)", MUTED, None), ("控制 / 配置注入", C["ctl"], "6,4"), ("后台维护", C["mgmt"], "2,4")]
lx = W - M
for lb, col, dash in reversed(leg):
    lx -= tw(lb, 12) + 52
    d = f' stroke-dasharray="{dash}"' if dash else ''
    o.append(f'<line x1="{lx}" y1="45" x2="{lx + 30}" y2="45" stroke="{col}" stroke-width="2.2"{d}/>')
    text(lx + 38, 49, lb, 12, SUB)

TOP = 104

# ================================================================== 中：数据平面
DP_IDX = len(o)
text(CX + 6, TOP + 26, "数据平面 · DATA PLANE", 13, C["cap"], weight=800, mono=True)
text(CX + CW, TOP + 26, "workers 模式下，以下每一层都跑在同一个 Worker 线程里（每个线程一份，线程数 ≈ CPU 核数）",
     12, MUTED, "end")


def layer(y, h, num, title, en, file_hint, color, shadow=True):
    rect(CX, y, CW, h, SURFACE, stroke=tint(color, 0.45), sw=1.2, r=14, shadow=shadow)
    rect(CX, y, STRIP, h, tint(color, 0.09), r=14)
    rect(CX + STRIP - 14, y, 14, h, tint(color, 0.09), r=0)
    o.append(f'<rect x="{CX}" y="{y + 12}" width="4" height="{h - 24}" rx="2" fill="{color}"/>')
    badge(CX + 16, y + 14, num, color)
    text(CX + 54, y + 34, title, 16, INK, weight=800)
    text(CX + 16, y + 64, en, 10.5, color, weight=700, mono=True)
    for i, fh in enumerate(file_hint):
        text(CX + 16, y + 84 + i * 16, fh, 10.5, MUTED, mono=True)


BX = CX + STRIP + 18                 # 层内容起点
BW = CW - STRIP - 36
GAP = 30

# -- L0 流量来源
y = TOP + 44
h = 62
rect(CX, y, CW, h, tint(C["src"], 0.06), stroke=tint(C["src"], 0.3), r=14)
text(CX + 16, y + 26, "流量来源", 15, INK, weight=800)
text(CX + 16, y + 46, "TRAFFIC SOURCE", 10.5, C["src"], weight=700, mono=True)
srcs = [("网卡 NIC（旁路镜像 / SPAN）", "IDS"), ("内核 Netfilter 队列 / inline 双网卡", "IPS"), ("离线 pcap 文件", "回放")]
sx = BX
for lb, tag in srcs:
    wbox = (BW - 28) / 3
    rect(sx, y + 13, wbox, 36, SURFACE, stroke=LINE, r=9)
    text(sx + 14, y + 36, lb, 12.5, INK, weight=600)
    chip(sx + wbox - tw(tag, 10.5) - 34, y + 21, tag, C["src"], 10.5, 20, filled=True)
    sx += wbox + 14
arrow(CX + CW / 2, y + h + 2, CX + CW / 2, y + h + GAP - 4, C["cap"], 2.4)

# -- L1 采集
y = y + h + GAP
h = 132
layer(y, h, "1", "包采集", "RECEIVE / CAPTURE", ["source-*.c", "tmqh-packetpool.c"], C["cap"])
text(BX, y + 28, "每种抓包方式 = 一对 TmModule：Receive* 负责取帧，Decode* 负责交给解码器；取到的字节装进预分配的 Packet", 12.5, SUB)
cap = ["AF_PACKET", "AF_XDP", "DPDK", "Netmap", "PF_RING", "libpcap", "pcap-file", "NFQ", "IPFW", "WinDivert", "NFLOG", "ERF/DAG"]
chips(BX, y + 44, cap, C["cap"], 6, 10.5, max_x=BX + BW)
bx2 = BX
for t, s in [("TmThreadsSlotPktAcqLoop()", "tm-threads.c · 采集线程主循环"),
             ("PacketPoolGetPacket()", "每线程 Packet 池，避免逐包 malloc")]:
    rect(bx2, y + 90, (BW - 14) / 2, 32, tint(C["cap"], 0.05), stroke=tint(C["cap"], 0.3), r=8)
    text(bx2 + 12, y + 111, t, 12, C["cap"], weight=700, mono=True)
    text(bx2 + (BW - 14) / 2 - 12, y + 111, s, 11.5, SUB, "end")
    bx2 += (BW - 14) / 2 + 14
arrow(CX + CW / 2, y + h + 2, CX + CW / 2, y + h + GAP - 4, C["dec"], 2.4)
text(CX + CW / 2 + 12, y + h + 20, "Packet *p", 11, MUTED, mono=True)

# -- L2 解码
y = y + h + GAP
h = 112
layer(y, h, "2", "解码与分片重组", "DECODE & DEFRAG", ["decode-*.c", "defrag*.c"], C["dec"])
steps = ["Ethernet", "VLAN / QinQ", "IPv4 · IPv6", "TCP · UDP · ICMP · SCTP"]
dx = BX
for i, s in enumerate(steps):
    wv = chip(dx, y + 16, s, C["dec"], 12, 28, filled=(i == 0))
    dx += wv
    if i < len(steps) - 1:
        arrow(dx + 4, y + 30, dx + 22, y + 30, C["dec"], 1.8)
        dx += 28
text(dx + 18, y + 35, "逐层剥头、校验、填 Packet 字段", 12, SUB)
text(BX, y + 70, "隧道回灌", 12, INK, weight=700)
chips(BX + 64, y + 55, ["GRE", "VXLAN", "Geneve", "MPLS", "Teredo", "IP-in-IP"], C["dec"], 6, 11)
rbx = BX + BW - 300
rect(rbx, y + 52, 300, 50, tint(C["dec"], 0.06), stroke=tint(C["dec"], 0.35), r=9)
text(rbx + 12, y + 72, "Defrag() · IP 分片重组", 12, C["dec"], weight=700, mono=True)
text(rbx + 12, y + 91, "分片先攒齐，重组成完整伪包再往下走", 11.5, SUB)
text(BX, y + 98, "内层包作为 tunnel pseudo packet 重新走一遍解码", 11, MUTED)
arrow(CX + CW / 2, y + h + 2, CX + CW / 2, y + h + GAP - 4, C["flow"], 2.4)

# -- L3 FlowWorker
y = y + h + GAP
h = 312
FW_Y, FW_H = y, h
rect(CX, y, CW, h, SURFACE, stroke=tint(C["flow"], 0.45), sw=1.2, r=14, shadow=True)
rect(CX, y, CW, 48, tint(C["flow"], 0.09), r=14)
rect(CX, y + 34, CW, 14, tint(C["flow"], 0.09), r=0)
badge(CX + 16, y + 9, "3", C["flow"])
text(CX + 54, y + 30, "FlowWorker", 16, INK, weight=800)
text(CX + 160, y + 30, "flow-worker.c · FlowWorker()", 11, C["flow"], weight=700, mono=True)
text(CX + CW - 16, y + 30, "引擎的心脏：一个包在同一个线程里依次经过下面五个子阶段", 12, SUB, "end")
subs = [
    ("Flow", "流跟踪", C["flow"], "FlowHandlePacket()", "flow.c · flow-hash.c",
     ["按五元组哈希查找 / 新建 Flow", "绑定 p->flow，更新状态与计时", "流表全局共享，按行加锁"]),
    ("Stream", "TCP 重组", C["stream"], "StreamTcp()", "stream-tcp*.c",
     ["TCP 状态机：握手 / 挥手 / RST", "乱序、重传、重叠、gap 处理", "攒够字节后回调应用层"]),
    ("AppLayer", "应用层解析", C["app"], "AppLayerHandleTCPData()", "app-layer*.c · rust/src/",
     ["协议识别：端口 + 内容 probing", "AppLayerParserParse()", "字节流 → 事务 (tx) 与字段"]),
    ("Detect", "规则检测", C["det"], "Detect()", "detect*.c",
     ["按包/流挑出候选规则组 SGH", "MPM 预过滤 → 逐条完整匹配", "命中则挂到 p->alerts"]),
    ("Output", "日志输出", C["out"], "OutputLoggerLog()", "output*.c",
     ["packet/tx/file/flow 等 logger", "告警、协议元数据写成事件", "在同一线程内同步调用"]),
]
n = len(subs)
ag = 26
FX, FWD = CX + 18, CW - 36
sw_ = (FWD - (n - 1) * ag) / n
sx = FX
sy = y + 70
sh = 196
for i, (name, cn, col, fn, files, pts) in enumerate(subs):
    rect(sx, sy, sw_, sh, SURFACE, stroke=tint(col, 0.5), sw=1.3, r=12, shadow=True)
    rect(sx, sy, sw_, 46, tint(col, 0.12), r=12)
    rect(sx, sy + 34, sw_, 12, tint(col, 0.12), r=0)
    text(sx + 12, sy + 21, f"3.{i + 1}", 10.5, col, weight=800, mono=True)
    text(sx + 12, sy + 39, name, 15, INK, weight=800)
    text(sx + sw_ - 12, sy + 39, cn, 12.5, col, "end", 700)
    text(sx + 12, sy + 68, fn, 11, col, weight=700, mono=True)
    text(sx + 12, sy + 85, files, 10, MUTED, mono=True)
    o.append(f'<line x1="{sx + 12}" y1="{sy + 96}" x2="{sx + sw_ - 12}" y2="{sy + 96}" stroke="{LINE}"/>')
    for j, pt in enumerate(pts):
        o.append(f'<circle cx="{sx + 16}" cy="{sy + 117 + j * 22 - 4}" r="2.6" fill="{col}"/>')
        text(sx + 25, sy + 117 + j * 22, pt, 11.5, SUB)
    if i < n - 1:
        arrow(sx + sw_ + 3, sy + sh / 2, sx + sw_ + ag - 3, sy + sh / 2, col, 2.2)
    sx += sw_ + ag
# UDP 旁路
s2x = FX + (sw_ + ag) * 1
ux1, ux2 = FX + sw_ / 2, FX + (sw_ + ag) * 2 + sw_ / 2
uy = sy + sh + 20
path(f"M {ux1} {sy + sh} L {ux1} {uy} L {ux2} {uy} L {ux2} {sy + sh + 3}", C["app"], 1.6, "5,4", "ah_app")
rect(s2x + 10, uy - 11, sw_ - 20, 22, tint(C["app"], 0.1), r=11)
text(s2x + sw_ / 2, uy + 4, "UDP 跳过重组 · AppLayerHandleUdp()", 10.5, C["app"], "middle", 700)
text(FX + (sw_ + ag) * 3, uy + 4, "每个包都会进 Detect；tx 类日志只在事务完成时输出", 11, MUTED)
arrow(CX + CW / 2, y + h + 2, CX + CW / 2, y + h + GAP - 4, C["ips"], 2.4)

# -- L4 裁决与出口
y = y + h + GAP
h = 150
layer(y, h, "4", "裁决与出口", "VERDICT & EGRESS", ["respond-reject.c", "output-json*.c"], C["ips"])
half = (BW - 18) / 2
rect(BX, y + 14, half, h - 28, tint(C["ips"], 0.05), stroke=tint(C["ips"], 0.35), r=10)
text(BX + 14, y + 38, "IPS inline：放行 / 丢弃", 13.5, INK, weight=800)
text(BX + 14, y + 60, "命中 drop 规则 → PacketDrop()，Verdict* 模块回写内核", 11.5, SUB)
chips(BX + 14, y + 74, ["NFQ Verdict", "IPFW Verdict", "AF_PACKET copy-mode", "reject → RST/ICMP"], C["ips"], 6, 10.5,
      max_x=BX + half - 10)
ox = BX + half + 18
rect(ox, y + 14, half, h - 28, tint(C["out"], 0.05), stroke=tint(C["out"], 0.35), r=10)
text(ox + 14, y + 38, "事件落地", 13.5, INK, weight=800)
text(ox + 14, y + 60, "EVE JSON 统一事件流：alert · flow · http · dns · tls · fileinfo · stats …", 11.5, SUB)
chips(ox + 14, y + 74, ["eve.json", "fast.log", "pcap-log", "syslog", "Redis", "unix socket"], C["out"], 6, 10.5,
      max_x=ox + half - 10)
DP_BOTTOM = y + h
rect(CX - 12, TOP, CW + 24, DP_BOTTOM - TOP + 14, tint(C["cap"], 0.035), stroke=tint(C["cap"], 0.25), r=18, dash="5,5")
o.insert(DP_IDX, o.pop())

# ================================================================== 左：启动与控制平面
def panel(x, y, w, h, title, en, color):
    rect(x, y, w, h, SURFACE, stroke=tint(color, 0.4), sw=1.2, r=14, shadow=True)
    rect(x, y, w, 44, tint(color, 0.10), r=14)
    rect(x, y + 30, w, 14, tint(color, 0.10), r=0)
    text(x + 16, y + 28, title, 15, INK, weight=800)
    text(x + w - 16, y + 28, en, 10, color, "end", 700, True)


text(LX + 4, TOP + 26, "控制平面 · CONTROL PLANE", 13, C["ctl"], weight=800, mono=True)
py = TOP + 44
panel(LX, py, LW, 330, "启动流程", "main.c", C["ctl"])
boot = [("SuricataPreInit()", "全局上下文初始化"), ("SCParseCommandLine()", "解析 -i / -r / -c 等参数"),
        ("SCLoadYamlConfig()", "suricata.yaml → 配置树"), ("SuricataInit()", "注册模块、加载规则、建线程"),
        ("SuricataPostInit()", "等所有线程就绪"), ("SuricataMainLoop()", "主线程处理信号与重载")]
for i, (fn, d) in enumerate(boot):
    by = py + 60 + i * 44
    o.append(f'<circle cx="{LX + 26}" cy="{by + 8}" r="9" fill="{tint(C["ctl"], 0.15)}" stroke="{C["ctl"]}" stroke-width="1.4"/>')
    text(LX + 26, by + 12, str(i + 1), 10, C["ctl"], "middle", 800, True)
    if i < len(boot) - 1:
        o.append(f'<line x1="{LX + 26}" y1="{by + 18}" x2="{LX + 26}" y2="{by + 43}" stroke="{tint(C["ctl"], 0.4)}" stroke-width="1.4"/>')
    text(LX + 44, by + 11, fn, 12, C["ctl"], weight=700, mono=True)
    text(LX + 44, by + 29, d, 11.5, SUB)

py += 330 + 18
RUL_Y = py
panel(LX, py, LW, 280, "规则加载与热更新", "detect-engine*.c", C["det"])
rl = [("*.rules", "规则文本"), ("SigLoadSignatures()", "解析为 Signature / SigMatch"),
      ("SigGroupBuild()", "规则分组 SGH + 编译 MPM"), ("DetectEngineCtx", "只读共享，所有 Worker 读同一份")]
for i, (fn, d) in enumerate(rl):
    by = py + 56 + i * 50
    rect(LX + 16, by, LW - 32, 40, tint(C["det"], 0.06) if i < 3 else tint(C["det"], 0.16),
         stroke=tint(C["det"], 0.35), r=8)
    text(LX + 28, by + 17, fn, 11.5, C["det"], weight=700, mono=True)
    text(LX + 28, by + 33, d, 10.5, SUB)
    if i < len(rl) - 1:
        arrow(LX + LW - 40, by + 40, LX + LW - 40, by + 49, C["det"], 1.4)
text(LX + 16, py + 270, "DetectEngineReload()：新建 de_ctx 后原子切换", 11, MUTED)

py += 280 + 18
panel(LX, py, LW, DP_BOTTOM - py, "运维控制通道", "unix-manager.c", C["ctl"])
text(LX + 16, py + 66, "suricatasc ⇄ Unix Socket", 12.5, INK, weight=700, mono=True)
chips(LX + 16, py + 80, ["reload-rules", "dump-counters", "iface-stat", "pcap-file"], C["ctl"], 6, 10.5,
      max_x=LX + LW - 12)
text(LX + 16, py + 158, "SIGUSR2 同样触发规则热加载", 11.5, SUB)
text(LX + 16, py + 178, "由主线程 / UnixManager 线程处理", 11, MUTED)

# 规则 → Detect 的注入线
det_x = FX + (sw_ + ag) * 3 + sw_ / 2
path(f"M {LX + LW} {RUL_Y + 226} L {CX - 20} {RUL_Y + 226} L {CX - 20} {FW_Y + FW_H + 12} "
     f"L {det_x} {FW_Y + FW_H + 12} L {det_x} {FW_Y + FW_H - 6}", C["ctl"], 1.8, "6,4", "ah_ctl")
rect(CX + 190, FW_Y + FW_H + 1, 200, 22, SURFACE, stroke=tint(C["ctl"], 0.4), r=11)
text(CX + 290, FW_Y + FW_H + 16, "规则 de_ctx 注入 Detect", 11, C["ctl"], "middle", 700)

# ================================================================== 右：管理线程与共享状态
text(RX + 4, TOP + 26, "后台 · MANAGEMENT", 13, C["mgmt"], weight=800, mono=True)
py = TOP + 44
panel(RX, py, RW, 310, "管理线程", "TMM_* 非包线程", C["mgmt"])
mg = [("FlowManager", "扫流表，超时的流标记淘汰"), ("FlowRecycler", "输出 flow 日志并归还内存"),
      ("BypassedFlowManager", "维护 eBPF/硬件 bypass 的流"), ("StatsLogger", "周期汇总计数器 → stats"),
      ("DetectLoader", "多线程并行加载规则"), ("UnixManager", "处理 suricatasc 命令")]
for i, (t, d) in enumerate(mg):
    by = py + 58 + i * 41
    rect(RX + 16, by, RW - 32, 34, tint(C["mgmt"], 0.05), stroke=tint(C["mgmt"], 0.25), r=8)
    text(RX + 28, by + 15, t, 11.5, C["mgmt"], weight=700, mono=True)
    text(RX + 28, by + 29, d, 10.5, SUB)

py += 310 + 18
SH_Y = py
panel(RX, py, RW, 262, "共享状态", "跨线程共享", C["flow"])
st = [("Flow 哈希表", "flow-hash.c", "按行加锁，Worker 与 FlowManager 共用"),
      ("DetectEngineCtx", "detect-engine.c", "只读，热更新时整体替换"),
      ("Host / IPPair 表", "host.c · ippair.c", "xbits、阈值、信誉等主机级状态"),
      ("Datasets", "datasets.c", "规则可读写的大规模集合")]
for i, (t, f_, d) in enumerate(st):
    by = py + 58 + i * 50
    rect(RX + 16, by, RW - 32, 42, tint(C["flow"], 0.05), stroke=tint(C["flow"], 0.3), r=8)
    text(RX + 28, by + 17, t, 12, INK, weight=700)
    text(RX + RW - 28, by + 17, f_, 10, MUTED, "end", mono=True)
    text(RX + 28, by + 34, d, 10.5, SUB)

py += 262 + 18
panel(RX, py, RW, DP_BOTTOM - py, "运行模式", "runmode-*.c", C["cap"])
rm = [("workers", "每线程跑完整条流水线（推荐）", "[R→D→FW→O]  ×N"),
      ("autofp", "采集线程按流哈希分发给处理线程", "[R→D] ⇒ queue ⇒ [FW→O] ×N"),
      ("single", "单线程，调试与离线分析", "[R→D→FW→O]  ×1")]
for i, (t, d, pic) in enumerate(rm):
    by = py + 58 + i * 62
    chip(RX + 16, by, t, C["cap"], 11.5, 22, filled=(i == 0))
    text(RX + 16 + tw(t, 11.5) + 30, by + 16, d, 11, SUB)
    text(RX + 16, by + 42, pic, 10.5, MUTED, mono=True)

# 管理线程 ↔ 流表 维护线
path(f"M {RX} {SH_Y + 79} L {CX + CW + 13} {SH_Y + 79} L {CX + CW + 13} {FW_Y + 55} L {FX + sw_ / 2} {FW_Y + 55} "
     f"L {FX + sw_ / 2} {FW_Y + 59}",
     C["mgmt"], 1.6, "2,4", "ah_mgmt")
rect(CX + CW - 250, FW_Y + 45, 200, 20, SURFACE, stroke=tint(C["mgmt"], 0.4), r=11)
text(CX + CW - 150, FW_Y + 59, "FlowManager 扫描超时 Flow", 11, C["mgmt"], "middle", 700)

# ================================================================== 底：基础设施
by = DP_BOTTOM + 30
bh = 100
rect(M, by, W - 2 * M, bh, "#2b3340", r=16, shadow=True)
text(M + 22, by + 32, "基础设施层", 16, "#ffffff", weight=800)
text(M + 22, by + 52, "FOUNDATION", 10.5, "#9fb0c8", weight=700, mono=True)
base = [
    ("线程框架", "tm-threads.c · tm-modules.c", "ThreadVars + TmSlot 串起模块"),
    ("多模式匹配 MPM", "util-mpm-hs.c · util-mpm-ac*.c", "Hyperscan / AC / AC-KS"),
    ("配置系统", "conf.c · conf-yaml-loader.c", "YAML → 树形 SCConfNode"),
    ("Rust 组件", "rust/src/", "HTTP2 · DNS · QUIC · SMB 等解析器"),
    ("内存与池", "util-pool*.c · util-hash*.c", "Packet/Flow 预分配 + memcap"),
    ("扩展", "util-lua*.c · util-ebpf.c", "Lua 脚本 · eBPF/XDP bypass"),
]
bx = M + 190
bw = (W - 2 * M - 190 - 22 - 5 * 12) / 6
for t, f_, d in base:
    rect(bx, by + 12, bw, bh - 24, "#384354", stroke="#4a566a", r=10)
    text(bx + 14, by + 36, t, 13.5, "#ffffff", weight=700)
    text(bx + 14, by + 56, f_, 10, "#9fb0c8", mono=True)
    text(bx + 14, by + 76, d, 11, "#d5dde8")
    bx += bw + 12

H = by + bh + 34
text(M, H - 12, "Suricata 源码阅读系列 · 函数名与文件名均对照 v8.0.7 源码核实 · 图中线程关系以 workers 运行模式为准", 11.5, MUTED)

# ------------------------------------------------------------------ 输出
def marker(mid, col):
    return (f'<marker id="{mid}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" '
            f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{col}"/></marker>')


defs = ('<defs><filter id="sh" x="-10%" y="-10%" width="120%" height="130%">'
        '<feDropShadow dx="0" dy="2" stdDeviation="4" flood-color="#1a1a1a" flood-opacity="0.08"/></filter>'
        + marker("ah", MUTED) + marker("ah_ctl", C["ctl"]) + marker("ah_mgmt", C["mgmt"]) + marker("ah_app", C["app"])
        + "".join(marker(f"ah{k}", v) for k, v in C.items()) + '</defs>')
# 彩色实线箭头使用各自颜色的 marker
body = "".join(o)
for k, v in C.items():
    body = body.replace(f'stroke="{v}" stroke-width="2.4" marker-end="url(#ah)"', f'stroke="{v}" stroke-width="2.4" marker-end="url(#ah{k})"')
    body = body.replace(f'stroke="{v}" stroke-width="2.2" marker-end="url(#ah)"', f'stroke="{v}" stroke-width="2.2" marker-end="url(#ah{k})"')
    body = body.replace(f'stroke="{v}" stroke-width="1.8" marker-end="url(#ah)"', f'stroke="{v}" stroke-width="1.8" marker-end="url(#ah{k})"')
    body = body.replace(f'stroke="{v}" stroke-width="1.4" marker-end="url(#ah)"', f'stroke="{v}" stroke-width="1.4" marker-end="url(#ah{k})"')

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
       f'font-family="-apple-system,\'PingFang SC\',\'Hiragino Sans GB\',\'Microsoft YaHei\',\'Segoe UI\',sans-serif">'
       + defs + f'<rect width="{W}" height="{H}" fill="{PAGE}"/>' + body + '</svg>')
with open(OUT, 'w', encoding='utf-8') as f:
    f.write(svg)
print("wrote", OUT, "H =", H)
