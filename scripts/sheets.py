#!/usr/bin/env python3
"""Timestamped contact sheets of a recording.

usage: sheets.py <recording> <outdir> <duration_seconds>

Writes overview-<n>.jpg (one thumbnail per minute, or finer for short
recordings) and detail-<n>.jpg (one per 10 seconds, 20 minutes per sheet).
Each thumbnail carries its mm:ss so a frame can be fetched at full resolution
with frame.sh afterwards.
"""
import math
import os
import shutil
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw, ImageFont

rec, out, dur = sys.argv[1], sys.argv[2], float(sys.argv[3])
os.makedirs(out, exist_ok=True)
COLS, THUMB_W, LABEL_H, PAD = 10, 320, 18, 4


def font():
    for name in ("Liberation Sans", "DejaVu Sans", "Noto Sans", "sans"):
        try:
            path = subprocess.run(["fc-match", "-f", "%{file}", name], capture_output=True, text=True).stdout.strip()
            if path:
                return ImageFont.truetype(path, 13)
        except Exception:
            pass
    try:
        return ImageFont.load_default(size=13)
    except TypeError:
        return ImageFont.load_default()


FONT = font()


def thumbs(interval, start, length, tmp):
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-ss", str(start), "-t", str(length), "-i", rec,
         "-vf", f"fps=1/{interval},scale={THUMB_W}:-1", "-q:v", "5", os.path.join(tmp, "t_%05d.jpg")],
        check=True,
    )
    return sorted(os.path.join(tmp, f) for f in os.listdir(tmp) if f.startswith("t_"))


def sheet(files, interval, start, path):
    if not files:
        return
    ims = [Image.open(f) for f in files]
    w, h = ims[0].size
    rows = math.ceil(len(ims) / COLS)
    S = Image.new("RGB", (COLS * (w + PAD) + PAD, rows * (h + LABEL_H + PAD) + PAD), "white")
    d = ImageDraw.Draw(S)
    for i, im in enumerate(ims):
        r, c = divmod(i, COLS)
        x, y = PAD + c * (w + PAD), PAD + r * (h + LABEL_H + PAD)
        S.paste(im.resize((w, h)), (x, y))
        t = int(start + i * interval)
        d.text((x + 2, y + h + 2), f"{t // 60:02d}:{t % 60:02d}", fill="black", font=FONT)
    S.save(path, quality=85)
    print(f"sheet: {path} ({len(ims)} thumbs, every {interval}s from {int(start)//60:02d}:{int(start)%60:02d})")


# Overview: one thumb per minute for long recordings, finer for short ones.
ov = 60 if dur > 1200 else (20 if dur > 300 else 5)
tmp = tempfile.mkdtemp()
try:
    sheet(thumbs(ov, 0, dur, tmp), ov, 0, os.path.join(out, "overview.jpg"))
finally:
    shutil.rmtree(tmp)

# Detail: one thumb per 10 s, 20-minute chunks (120 thumbs a sheet).
if dur > 300:
    chunk = 1200
    for n, start in enumerate(range(0, int(dur), chunk), 1):
        tmp = tempfile.mkdtemp()
        try:
            sheet(thumbs(10, start, min(chunk, dur - start), tmp), 10, start, os.path.join(out, f"detail-{n}.jpg"))
        finally:
            shutil.rmtree(tmp)
