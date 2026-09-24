# -*- coding: utf-8 -*-
import os

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'images')

W = 1700

INK = "#0b0b0b"
SUB = "#52514e"
MUTED = "#898781"
SURFACE = "#fcfcfb"
PAGE = "#f2f1ec"
BORDER = "rgba(11,11,11,0.10)"

C = {
    "blue":    "#2a78d6",
    "orange":  "#eb6834",
    "aqua":    "#1baf7a",
    "yellow":  "#c98500",   # darker step for text-on-white legibility
    "magenta": "#c2527a",   # darker step for text-on-white legibility
    "green":   "#008300",
    "violet":  "#4a3aa7",
    "red":     "#c23b3b",
}

def tint(hex_color, ratio=0.12):
    hex_color = hex_color.lstrip('#')
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    r = int(r*ratio + 255*(1-ratio))
    g = int(g*ratio + 255*(1-ratio))
    b = int(b*ratio + 255*(1-ratio))
    return f"#{r:02x}{g:02x}{b:02x}"

def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def wrap(s, max_chars):
    """Word-aware greedy wrap: ASCII runs stay atomic, CJK chars are their own token."""
    tokens = []
    cur = ""
    for ch in s:
        if ch == ' ':
            if cur:
                tokens.append(cur); cur = ""
            tokens.append(' ')
        elif ord(ch) < 128:
            cur += ch
        else:
            if cur:
                tokens.append(cur); cur = ""
            tokens.append(ch)
    if cur:
        tokens.append(cur)

    lines = []
    line = ""
    line_len = 0
    for tok in tokens:
        tok_w = sum(1.0 if ord(c) < 128 else 1.7 for c in tok)
        if line_len + tok_w > max_chars and line.strip():
            lines.append(line.rstrip())
            line, line_len = "", 0
        if tok == ' ' and line == "":
            continue
        line += tok
        line_len += tok_w
    if line.strip():
        lines.append(line.rstrip())
    return lines

parts = []
defs = []
defs.append('<filter id="softshadow" x="-30%" y="-30%" width="160%" height="160%"><feDropShadow dx="0" dy="2" stdDeviation="5" flood-color="#0b0b0b" flood-opacity="0.10"/></filter>')

def rect(x, y, w, h, fill, radius=13, stroke=BORDER, sw=1, shadow=True, dashed=False):
    dash = ' stroke-dasharray="6,4"' if dashed else ''
    filt = ' filter="url(#softshadow)"' if shadow else ''
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{dash}{filt}/>'

def text(x, y, s, size=13, color=SUB, anchor="start", weight="400", family=None, ls=None):
    fam = f' font-family="{family}"' if family else ''
    letter = f' letter-spacing="{ls}"' if ls else ''
    return f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" fill="{color}" font-weight="{weight}"{fam}{letter}>{esc(s)}</text>'

def para(x, y, s, max_chars, size=13, color=SUB, line_h=18):
    lines = wrap(s, max_chars)
    out = []
    for i, ln in enumerate(lines):
        out.append(text(x, y + i*line_h, ln, size, color))
    return ''.join(out), len(lines)*line_h

MONO = "'SFMono-Regular','Consolas','Menlo',monospace"

# ---------- header (compact) ----------
head_h = 100
parts.append(rect(0, 0, W, head_h, SURFACE, radius=0, shadow=False, stroke="none"))
parts.append(f'<rect x="40" y="20" width="56" height="56" rx="14" fill="{C["orange"]}" filter="url(#softshadow)"/>')
parts.append(text(68, 57, "S", 28, "#ffffff", "middle", "700"))
parts.append(text(112, 46, "SURICATA", 28, INK, "start", "800"))
parts.append(f'<rect x="310" y="27" width="188" height="23" rx="11.5" fill="{tint(C["orange"],0.16)}"/>')
parts.append(text(404, 43, "v9.0.0-dev ENGINE SPEC", 11.5, C["orange"], "middle", "700", MONO))
parts.append(text(112, 70, "开源多线程网络威胁检测引擎 · IDS / IPS / NSM", 13.5, SUB))
parts.append(text(112, 88, "源码阅读系列配套架构总览 —— 每个模块都能在 src/ 里找到对应文件；标红边框的三张卡片是系列公认的难点", 11.5, MUTED))

def pill(x, y, w, h, label, value, accent):
    s = rect(x, y, w, h, SURFACE, radius=11, stroke="#e1e0d9")
    s += text(x+16, y+19, label, 9.5, MUTED, weight="700", family=MONO, ls="0.5px")
    s += text(x+16, y+38, value, 13.5, INK, weight="700")
    return s

parts.append(pill(1220, 20, 220, 56, "RUN MODES", "Workers / AutoFP / Single", C["blue"]))
parts.append(pill(1450, 20, 210, 56, "DEFAULT MPM", "Hyperscan (auto)", C["magenta"]))

parts.append(f'<line x1="0" y1="{head_h}" x2="{W}" y2="{head_h}" stroke="#e1e0d9" stroke-width="1.5"/>')

# ---------- layout ----------
margin = 36
top0 = head_h + 22
left_x = margin
left_w = 1000
gap = 24
right_x = left_x + left_w + gap
right_w = W - right_x - margin
CARD_GAP = 16

def card_header(x, y, w, num, title, eyebrow, accent, highlight, num_w=38):
    s = ''
    if num:
        s += f'<rect x="{x+20}" y="{y+18}" width="{num_w}" height="{num_w}" rx="9" fill="{tint(accent,0.14)}"/>'
        s += text(x+20+num_w/2, y+18+num_w/2+5.5, num, 14.5, accent, "middle", "800", MONO)
        title_x = x + 20 + num_w + 14
    else:
        title_x = x + 20
    s += text(title_x, y+36, title, 17.5, INK, weight="800")
    eyebrow_full = ("★ 重难点 · " + eyebrow) if highlight else eyebrow
    s += text(x+w-20, y+33, eyebrow_full, 11, accent, "end", "700", MONO, "0.3px")
    return s

def tagbox(x, y, w, h, title, sub, accent):
    s = rect(x, y, w, h, tint(accent, 0.06), radius=9, stroke=tint(accent, 0.35), shadow=False)
    s += text(x+13, y+20, title, 12, accent, weight="700", family=MONO)
    subtxt, _ = para(x+13, y+36, sub, int(w/6.2), 10.5, SUB, 14)
    s += subtxt
    return s

def bullet(x, y, s, accent, size=12):
    o = f'<circle cx="{x+4}" cy="{y-4}" r="3.5" fill="{accent}"/>'
    o += text(x+15, y, s, size, INK, weight="600", family=MONO)
    return o

body = []
y = top0

def pipeline_card(y, num, title, eyebrow, accent, desc, tags_fn, highlight=False):
    """Draws a numbered pipeline card with a dynamically-sized gap between the
    (possibly 2-line) description and whatever tags_fn draws below it.
    tags_fn(content_y) -> (svg_string, content_height); returns new y."""
    desc_y = y + 58
    d, dh = para(left_x+20, desc_y, desc, 78, 13, SUB, 18)
    content_y = desc_y + dh + 14
    tags_svg, tags_h = tags_fn(content_y)
    card_h = (content_y - y) + tags_h + 18
    fill = tint(accent, 0.04) if highlight else SURFACE
    stroke = accent if highlight else BORDER
    sw = 2 if highlight else 1
    card_svg = rect(left_x, y, left_w, card_h, fill, stroke=stroke, sw=sw)
    card_svg += card_header(left_x, y, left_w, num, title, eyebrow, accent, highlight)
    return card_svg + d + tags_svg, y + card_h + CARD_GAP

# ===== 01 Packet Acquisition =====
def tags01(ty):
    tags = [
        ("AF_PACKET", "Linux PACKET_MMAP 环形缓冲"),
        ("DPDK", "用户态轮询，零拷贝快速路径"),
        ("PF_RING", "经 libpcap 编译支持"),
        ("libpcap", "标准 PCAP API / 离线文件回放"),
        ("NFQ · Netmap", "NFQ 用于 IPS 内联，Netmap 零拷贝"),
    ]
    tw = (left_w - 40 - 4*14) / 5
    s, tx = '', left_x + 20
    for title, sub in tags:
        s += tagbox(tx, ty, tw, 66, title, sub, C["blue"])
        tx += tw + 14
    return s, 66

svg, y = pipeline_card(y, "01", "数据包采集层 Packet Acquisition", "CAPTURE & INGESTION", C["blue"],
    "从网卡、文件或内核旁路接口读取原始帧，是整条流水线的入口（第 3 篇细看这一层）。", tags01)
body.append(svg)

# ===== 02 Decode & Defrag =====
def tags02(ty):
    dec_w = left_w - 40 - 250 - 14
    s = tagbox(left_x+20, ty, dec_w, 48, "DECODERS", "Ethernet / VLAN·QinQ / IPv4·IPv6 / TCP·UDP·ICMP / GRE·VXLAN·Geneve·MPLS 隧道", C["orange"])
    s += tagbox(left_x+20+dec_w+14, ty, 250, 48, "IP Defrag Engine", "重组 IPv4 / IPv6 分片 (defrag-hash.c)", C["orange"])
    return s, 48

svg, y = pipeline_card(y, "02", "解码与分片重组 Decode & Defrag", "PROTOCOL VALIDATION", C["orange"],
    "逐层剥开协议头做基础校验，并在检测前把 IP 分片重新拼成完整包（第 4 篇细看这一层）。", tags02)
body.append(svg)

# ===== 03 Flow & Stream (重难点) =====
def tags03(ty):
    half = (left_w - 40 - 14) / 2
    s = tagbox(left_x+20, ty, half, 48, "Flow Table", "哈希表跟踪海量并发流，超时即回收", C["aqua"])
    s += tagbox(left_x+20+half+14, ty, half, 48, "Stream Reassembly", "处理乱序、重传、gap 与 evasion", C["aqua"])
    return s, 48

svg, y = pipeline_card(y, "03", "Flow 与 Stream 引擎", "STATE TRACKING", C["aqua"],
    "按五元组跟踪连接状态，重组乱序 TCP 字节流，再把结构化 payload 交给应用层解析器（第 5、6 篇）。", tags03,
    highlight=True)
body.append(svg)

# ===== 04 App Layer Parsers =====
def tags04(ty):
    protos = ["HTTP/1 & HTTP/2", "TLS / SSL", "DNS", "SMB / DCERPC",
              "SSH", "FTP / FTP-DATA", "SMTP / IMAP", "MQTT / NFS / RDP"]
    pcols = 4
    pw = (left_w - 40 - (pcols-1)*14) / pcols
    prow_h = 28
    s = ''
    for i, p in enumerate(protos):
        col, row = i % pcols, i // pcols
        px = left_x+20 + col*(pw+14)
        pyy = ty + 10 + row*(prow_h+6)
        s += bullet(px, pyy, p, C["yellow"])
    rows = (len(protos)+pcols-1)//pcols
    return s, 10 + rows*prow_h + (rows-1)*6 + 4

svg, y = pipeline_card(y, "04", "应用层解析框架", "APP-ID & PROTOCOL EXTRACT", C["yellow"],
    "probing parser 先识别端口/内容对应的协议，再用专门的解析器把字节流还原成结构化字段（第 7 篇）。", tags04)
body.append(svg)

# ===== 05 Detection Engine (重难点) =====
def tags05(ty):
    half = (left_w - 40 - 14) / 2
    s = tagbox(left_x+20, ty, half, 56, "PATTERN MATCHING", "Hyperscan（默认自动选用）与 Aho-Corasick(AC/AC-KS) 多模式匹配", C["magenta"])
    s += tagbox(left_x+20+half+14, ty, half, 56, "SIGNATURE ENGINE", "SigGroupHead 规则分组 + flowbits/flowint 状态标志位", C["magenta"])
    return s, 56

svg, y = pipeline_card(y, "05", "检测引擎", "MULTI-PATTERN MATCHER", C["magenta"],
    "规则加载后被编译成 Signature / SigMatch，靠多模式匹配把海量规则的搜索开销压下来（第 8、9 篇）。", tags05,
    highlight=True)
body.append(svg)

# ===== 06 Output =====
def tags06(ty):
    outs = [("EVE JSON", "统一结构化事件"), ("Fast Log", "单行经典告警格式"),
            ("PCAP Log", "落盘原始包"), ("Redis · Syslog", "外部流式转发")]
    ow = (left_w - 40 - 3*14) / 4
    s, ox = '', left_x+20
    for t, sub in outs:
        s += tagbox(ox, ty, ow, 48, t, sub, C["green"])
        ox += ow + 14
    return s, 48

svg, y = pipeline_card(y, "06", "输出与日志子系统", "JSON EVENTS / EVE", C["green"],
    "把告警、元数据、文件信息统一整理成结构化事件，写文件或转发到外部系统（第 10 篇）。", tags06)
body.append(svg)

left_bottom = y

# ================= RIGHT COLUMN =================
ry = top0

def side_card(ry, title, eyebrow, accent, desc, content_fn, desc_max=38, highlight=False):
    """Same dynamic-gap approach as pipeline_card, for the narrower right column."""
    desc_y = ry + 54
    d, dh = para(right_x+20, desc_y, desc, desc_max, 12.5, SUB, 17)
    content_y = desc_y + dh + 14
    content_svg, content_h = content_fn(content_y)
    card_h = (content_y - ry) + content_h + 18
    fill = tint(accent, 0.04) if highlight else SURFACE
    stroke = accent if highlight else BORDER
    sw = 2 if highlight else 1
    card_svg = rect(right_x, ry, right_w, card_h, fill, stroke=stroke, sw=sw)
    card_svg += card_header(right_x, ry, right_w, None, title, eyebrow, accent, highlight)
    return card_svg + d + content_svg, ry + card_h + CARD_GAP

# --- Multi-threading (重难点) ---
def content_thread(ty):
    rows = [
        ("Worker Threads", "Receive→Decode→FlowWorker→Output 全链路在一个线程里"),
        ("Flow Manager Thread", "清理超时的 flow"),
        ("Flow Recycler Thread", "回收已过期 flow 的内存"),
        ("Stats / LogMaintenance", "周期统计与日志轮转"),
    ]
    s = ''
    cy = ty
    for t, sub in rows:
        s += text(right_x+20, cy, t, 12.5, C["violet"], weight="700", family=MONO)
        sub_lines, sub_h = para(right_x+20, cy+16, sub, 38, 11, SUB, 14)
        s += sub_lines
        cy += 16 + sub_h + 7
    return s, cy - ty - 7

svg, ry = side_card(ry, "多线程模型", "WORKERS MODE", C["violet"],
    "workers 模式下每个线程独立跑完整条流水线；autofp 拆两组线程，中间用 flow 哈希队列接力（第 2 篇）。", content_thread,
    highlight=True)
body.append(svg)

# --- File extraction ---
def content_file(ty):
    fe = ["Magic Type Check", "MD5 / SHA256 Calc", "Storage Spool"]
    s, fx = '', right_x + 20
    for t in fe:
        tw2 = 11*len(t)*0.62 + 22
        s += rect(fx, ty, tw2, 24, tint(C["blue"],0.14), radius=12, stroke="none", shadow=False)
        s += text(fx+tw2/2, ty+16, t, 10, C["blue"], "middle", "700", MONO)
        fx += tw2 + 9
    return s, 24

svg, ry = side_card(ry, "文件提取模块", "STREAM ATTACHED", C["blue"],
    "从 HTTP / SMTP / FTP / SMB 等协议流里实时抽取文件并落盘。", content_file)
body.append(svg)

# --- Datasets & reputation ---
def content_dataset(ty):
    s = bullet(right_x+20, ty+4, "IP Reputation Rules (reputation.c)", C["red"], 11.5)
    s += bullet(right_x+20, ty+26, "Dynamic String / Hash Datasets", C["red"], 11.5)
    return s, 30

svg, ry = side_card(ry, "数据集与信誉", "DATASET MATCH", C["red"],
    "把 IP 信誉名单和通用数据集接入检测引擎，用于大规模值匹配。", content_dataset)
body.append(svg)

# --- Lua ---
def content_lua(ty):
    half = (right_w - 40 - 12) / 2
    s = tagbox(right_x+20, ty, half, 56, "Rule Match Hook", "detect-lua.c，rule 里的 lua 关键字", C["aqua"])
    s += tagbox(right_x+20+half+12, ty, half, 56, "Output Hook", "output-lua.c，自定义输出格式", C["aqua"])
    return s, 56

svg, ry = side_card(ry, "Lua 脚本引擎", "LUA 5.1", C["aqua"],
    "把 Suricata 内部状态暴露给用户脚本，用于自定义检测条件或日志加工。", content_lua)
body.append(svg)

right_bottom = ry

content_bottom = max(left_bottom, right_bottom)

# ---------- footer ----------
footer_h = 44
foot_y = content_bottom + 6
body.append(f'<line x1="{margin}" y1="{foot_y}" x2="{W-margin}" y2="{foot_y}" stroke="#e1e0d9" stroke-width="1.5"/>')
body.append(text(margin, foot_y+26, "Suricata 源码阅读系列 · 内容逐条对照 v9.0.0-dev 源码核实，不是营销资料", 11.5, MUTED))

legend = [("采集/解码", C["blue"]), ("核心引擎", C["aqua"]), ("应用层", C["yellow"]), ("模式匹配", C["magenta"])]
lx = W - margin
for label, color in reversed(legend):
    lw = 10*len(label)*1.05 + 20
    lx -= lw
    body.append(f'<circle cx="{lx+7}" cy="{foot_y+21}" r="4.5" fill="{color}"/>')
    body.append(text(lx+19, foot_y+25, label, 11, SUB))
    lx -= 12

H = int(foot_y + footer_h)

svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="-apple-system, \'Segoe UI\', \'PingFang SC\', \'Microsoft YaHei\', sans-serif">']
svg.extend(defs)
svg.append(rect(0, 0, W, H, PAGE, radius=0, shadow=False, stroke="none"))
svg.extend(parts)
svg.extend(body)
svg.append('</svg>')

with open(os.path.join(OUT_DIR, 'suricata-architecture-poster.svg'), 'w', encoding='utf-8') as f:
    f.write(''.join(svg))
print("H=", H)
