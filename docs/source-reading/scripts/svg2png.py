# -*- coding: utf-8 -*-
"""把 images/ 下的 SVG 导出成 2 倍分辨率的 PNG(用于公众号等不支持 SVG 的平台)。

用 Chrome 无头模式渲染，中文字体与浏览器显示一致；再量化到 256 色压缩体积。
依赖：Google Chrome(或用 CHROME 环境变量指定路径)、Pillow。

用法：
    python3 svg2png.py                      # 导出 images/ 下全部 SVG
    python3 svg2png.py ../images/a.svg ...  # 只导出指定文件
"""
import glob
import os
import re
import shutil
import subprocess
import sys
import tempfile

from PIL import Image

SCALE = 2
IMAGES = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'images')


def find_chrome():
    candidates = [
        os.environ.get('CHROME'),
        '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
        shutil.which('google-chrome'),
        shutil.which('chromium'),
    ]
    for c in candidates:
        if c and os.path.exists(c):
            return c
    sys.exit('找不到 Chrome，请用 CHROME 环境变量指定路径')


def svg_size(path):
    with open(path, encoding='utf-8') as f:
        head = f.read(2000)
    m = re.search(r'viewBox="\s*[-\d.]+[\s,]+[-\d.]+[\s,]+([\d.]+)[\s,]+([\d.]+)"', head)
    if not m:
        sys.exit(f'{path}: 没有 viewBox，无法确定尺寸')
    return round(float(m.group(1))), round(float(m.group(2)))


def export(chrome, svg):
    w, h = svg_size(svg)
    png = os.path.splitext(svg)[0] + '.png'
    with tempfile.TemporaryDirectory() as tmp:
        raw = os.path.join(tmp, 'raw.png')
        subprocess.run([
            chrome, '--headless=new', '--disable-gpu', '--hide-scrollbars',
            f'--force-device-scale-factor={SCALE}', f'--window-size={w},{h}',
            f'--screenshot={raw}', 'file://' + os.path.abspath(svg),
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        im = Image.open(raw).convert('RGB')
        im.quantize(colors=256, method=Image.Quantize.MEDIANCUT,
                    dither=Image.Dither.NONE).save(png, optimize=True)
    print(f'{os.path.basename(png)}  {im.size[0]}x{im.size[1]}  {os.path.getsize(png) // 1024} KB')


def main():
    svgs = sys.argv[1:] or sorted(glob.glob(os.path.join(IMAGES, '*.svg')))
    chrome = find_chrome()
    for svg in svgs:
        export(chrome, svg)


if __name__ == '__main__':
    main()
