#!/usr/bin/env python3
"""
gta6-clipper-01 — original neon Vice City chase clip, drawn frame-by-frame
with Pillow and encoded with ffmpeg. No downloaded footage, no copyrighted
video: every pixel is generated here.

Moment chosen: the first 8 seconds of GTA VI — a 5-star wanted chase down
Ocean Drive at night. After 13 years (GTA V 2013 -> GTA VI 2026) the game
opens mid-chase: police lights, palm silhouettes whipping past, a sports
car at full speed. It holds a muted Shorts viewer because 5 wanted stars
read instantly, neon pink/cyan stops the thumb, and opening on the action
leaves no dead air.

Hook (0-8s):  "GTA VI IS HERE" then "13 YEARS LATER"
Pitch (8-20s): "Make clips like this with AI and earn money on make.fun"
               "make.fun/bounty/gta6-clipper-01"
"""
import math
import os
import random
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
FPS = 30
SECONDS = 20
TOTAL = FPS * SECONDS
HERE = os.path.dirname(os.path.abspath(__file__))
FRAMES = os.path.join(HERE, "frames_tmp")
OUT = os.path.join(HERE, "clip.mp4")

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

random.seed(20261119)  # GTA VI launch day — deterministic art

# fixed starfield + building windows so they don't flicker between frames
STARS = [(random.randint(0, W), random.randint(0, 900), random.randint(1, 3)) for _ in range(140)]
BUILDINGS = []
x = -60
while x < W + 200:
    bw = random.randint(90, 210)
    bh = random.randint(260, 640)
    wins = [(random.randint(10, max(11, bw - 26)), random.randint(14, max(15, bh - 30)))
            for _ in range(random.randint(8, 26))]
    BUILDINGS.append((x, bw, bh, wins))
    x += bw + random.randint(6, 30)
BUILD_SPAN = x + 200


def font(size, bold=True):
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REG, size)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def draw_text_center(d, cx, cy, text, f, fill, stroke=10, stroke_fill=(10, 4, 24)):
    d.text((cx, cy), text, font=f, fill=fill, anchor="mm",
           stroke_width=stroke, stroke_fill=stroke_fill)


def draw_palm(d, x, base_y, hgt, lean, color):
    """Silhouette palm: curved trunk + fronds."""
    top_x = x + lean
    top_y = base_y - hgt
    pts = []
    for i in range(13):
        t = i / 12
        px = x + (top_x - x) * (t * t)
        py = base_y + (top_y - base_y) * t
        pts.append((px, py))
    d.line(pts, fill=color, width=16)
    for ang in (-2.6, -2.0, -1.3, -0.6, 0.0, 0.6):
        ex = top_x + math.cos(ang) * 150
        ey = top_y + math.sin(ang) * 90 + 46
        mx = top_x + math.cos(ang) * 84
        my = top_y + math.sin(ang) * 58 - 26
        d.line([(top_x, top_y), (mx, my), (ex, ey)], fill=color, width=11)


def draw_star(d, cx, cy, r, filled):
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + math.cos(ang) * rr, cy + math.sin(ang) * rr))
    if filled:
        d.polygon(pts, fill=(255, 214, 64), outline=(255, 245, 190), width=3)
    else:
        d.polygon(pts, outline=(200, 190, 220), width=3)


def draw_car(d, cx, cy, scale, bounce, police_flash):
    """Rear view sports car with headlight glow spilling forward (up-screen)."""
    w = int(430 * scale)
    h = int(210 * scale)
    y = cy + bounce
    # headlight cones (drawn first, behind the car body)
    for sx in (-1, 1):
        lx = cx + sx * int(w * 0.30)
        d.polygon([(lx, y - h // 2), (lx + sx * 60, y - int(h * 2.6)), (lx + sx * 230, y - int(h * 2.6))],
                  fill=(255, 240, 170, 34))
    # shadow
    d.ellipse([cx - w // 2 - 30, y + h // 2 - 26, cx + w // 2 + 30, y + h // 2 + 30], fill=(4, 2, 12))
    # body
    body = (20, 160, 200)  # neon cyan
    d.rounded_rectangle([cx - w // 2, y - h // 2, cx + w // 2, y + h // 2], radius=42, fill=body)
    d.rounded_rectangle([cx - w // 2 + 26, y - h // 2 + 12, cx + w // 2 - 26, y - h // 6], radius=30, fill=(16, 120, 160))
    # rear window + spoiler
    d.rounded_rectangle([cx - int(w * 0.28), y - h // 2 + 18, cx + int(w * 0.28), y - int(h * 0.18)], radius=18, fill=(10, 16, 40))
    d.rectangle([cx - w // 2 - 18, y - h // 2 - 26, cx + w // 2 + 18, y - h // 2 - 4], fill=(12, 12, 26))
    d.rectangle([cx - int(w * 0.34), y - h // 2 - 4, cx - int(w * 0.26), y - h // 2 + 22], fill=(12, 12, 26))
    d.rectangle([cx + int(w * 0.26), y - h // 2 - 4, cx + int(w * 0.34), y - h // 2 + 22], fill=(12, 12, 26))
    # taillights — full-width neon bar
    d.rounded_rectangle([cx - w // 2 + 18, y + int(h * 0.08), cx + w // 2 - 18, y + int(h * 0.08) + 26], radius=12, fill=(255, 45, 85))
    d.rounded_rectangle([cx - w // 2 + 18, y + int(h * 0.08) + 6, cx + w // 2 - 18, y + int(h * 0.08) + 14], radius=6, fill=(255, 150, 175))
    # plate
    d.rounded_rectangle([cx - 74, y + int(h * 0.24), cx + 74, y + int(h * 0.24) + 44], radius=8, fill=(240, 240, 235))
    d.text((cx, y + int(h * 0.24) + 22), "VC-2026", font=font(28), fill=(20, 20, 30), anchor="mm")
    # police light wash from behind — a tight glow right behind the car,
    # not a giant blob across the whole bottom of the frame
    if police_flash:
        col = (255, 60, 80, 42) if police_flash == 1 else (60, 110, 255, 42)
        d.ellipse([cx - 340, y + 30, cx + 340, y + 330], fill=col)


def render_frame(idx):
    t = idx / FPS
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img, "RGBA")

    # --- sky: deep purple up top melting into hot pink at the horizon ---
    horizon = 1180
    for yy in range(0, horizon, 8):
        k = yy / horizon
        col = lerp((16, 6, 44), (148, 32, 120), k ** 1.6)
        if k > 0.78:
            col = lerp(col, (255, 110, 140), (k - 0.78) / 0.22)
        d.rectangle([0, yy, W, yy + 8], fill=col)
    # stars + moon
    for (sx, sy, sr) in STARS:
        d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(255, 255, 255, 170))
    d.ellipse([W - 300, 130, W - 150, 280], fill=(255, 236, 200))
    d.ellipse([W - 268, 118, W - 128, 268], fill=(24, 10, 52))

    # --- skyline (slow parallax) ---
    off = int(t * 55) % BUILD_SPAN
    for (bx, bw, bh, wins) in BUILDINGS:
        for rep in (0, BUILD_SPAN):
            x0 = bx - off + rep
            if x0 + bw < -40 or x0 > W + 40:
                continue
            d.rectangle([x0, horizon - bh, x0 + bw, horizon], fill=(22, 10, 44))
            d.rectangle([x0, horizon - bh, x0 + bw, horizon - bh + 6], fill=(255, 80, 170))
            for (wx, wy) in wins:
                d.rectangle([x0 + wx, horizon - bh + wy, x0 + wx + 12, horizon - bh + wy + 16],
                            fill=(255, 214, 130))

    # --- ground + road in perspective ---
    d.rectangle([0, horizon, W, H], fill=(10, 6, 26))
    vx, vy = W // 2, horizon + 6
    d.polygon([(vx - 60, vy), (vx + 60, vy), (W + 240, H), (-240, H)], fill=(26, 22, 44))
    # neon road edges
    d.line([(vx - 60, vy), (-240, H)], fill=(255, 45, 160), width=10)
    d.line([(vx + 60, vy), (W + 240, H)], fill=(40, 220, 255), width=10)
    # moving centre dashes
    for i in range(9):
        k = ((i / 9) + (t * 0.85) % (1 / 9)) 
        yy = vy + (H - vy) * (k ** 1.7)
        wdt = 4 + k * 26
        ln = 10 + k * 90
        d.rectangle([vx - wdt / 2, yy, vx + wdt / 2, yy + ln], fill=(255, 240, 190))

    # --- foreground palms whipping past (fast parallax) ---
    palm_span = 2600
    poff = int(t * 620) % palm_span
    for i in range(7):
        px = i * 390 - poff
        for rep in (0, palm_span):
            xx = px + rep
            if -260 < xx < W + 260:
                side = 1 if (i % 2 == 0) else -1
                base = H - 60 - (i % 3) * 120
                draw_palm(d, xx, base, 560 + (i % 3) * 90, side * 90, (6, 3, 16))

    # --- speed lines ---
    rng = random.Random(idx)
    for _ in range(14):
        sy = rng.randint(900, 1750)
        sx = rng.randint(-100, W)
        ln = rng.randint(90, 320)
        d.line([(sx, sy), (sx + ln, sy)], fill=(255, 255, 255, rng.randint(40, 120)), width=4)

    # --- the car ---
    bounce = int(math.sin(t * 22) * 5)
    flash = 0
    if t > 1.2:
        flash = 1 if (idx // 5) % 2 == 0 else 2
    draw_car(d, W // 2, 1450, 1.0, bounce, flash)

    # --- wanted stars, top-right, filling up over the hook ---
    lit = min(5, 1 + int(t / 1.4))
    for i in range(5):
        draw_star(d, W - 470 + i * 92, 96, 38, filled=(i < lit))

    # --- text ---
    big = font(118)
    mid = font(92)
    if t < 4.0:
        # punch-in scale for the first beat
        s = 0.7 + 0.3 * min(1.0, t / 0.45)
        draw_text_center(d, W // 2, 430, "GTA VI", font(int(150 * s)), (255, 255, 255), stroke=14)
        draw_text_center(d, W // 2, 590, "IS HERE", font(int(150 * s)), (255, 80, 170), stroke=14)
    elif t < 8.0:
        draw_text_center(d, W // 2, 430, "13 YEARS", big, (255, 255, 255), stroke=13)
        draw_text_center(d, W // 2, 565, "LATER", big, (40, 220, 255), stroke=13)
        draw_text_center(d, W // 2, 700, "Vice City is back", font(58, bold=False), (255, 236, 200), stroke=7)
    else:
        # pitch: dim the action, card in the safe area (clear of bottom 15%)
        d.rectangle([0, 0, W, H], fill=(8, 4, 22, 150))
        card = [70, 560, W - 170, 1150]  # right edge kept clear for Shorts UI
        d.rounded_rectangle(card, radius=36, fill=(14, 8, 36, 235), outline=(255, 80, 170), width=6)
        if t < 14.0:
            draw_text_center(d, (card[0] + card[2]) // 2, 700, "Make clips like", mid, (255, 255, 255), stroke=9)
            draw_text_center(d, (card[0] + card[2]) // 2, 810, "this with AI", mid, (255, 255, 255), stroke=9)
            draw_text_center(d, (card[0] + card[2]) // 2, 930, "and earn money", font(76), (255, 214, 64), stroke=8)
            draw_text_center(d, (card[0] + card[2]) // 2, 1030, "on make.fun", font(76), (40, 220, 255), stroke=8)
        else:
            draw_text_center(d, (card[0] + card[2]) // 2, 720, "Start now:", font(72), (255, 255, 255), stroke=8)
            draw_text_center(d, (card[0] + card[2]) // 2, 855, "make.fun/bounty/", font(68), (255, 214, 64), stroke=8)
            draw_text_center(d, (card[0] + card[2]) // 2, 960, "gta6-clipper-01", font(74), (255, 80, 170), stroke=8)
            draw_text_center(d, (card[0] + card[2]) // 2, 1075, "$500 bounty", font(64), (255, 255, 255), stroke=7)

    return img


def main():
    os.makedirs(FRAMES, exist_ok=True)
    print(f"rendering {TOTAL} frames at {W}x{H} ...")
    for i in range(TOTAL):
        render_frame(i).save(os.path.join(FRAMES, f"f{i:05d}.png"))
        if i % 60 == 0:
            print(f"  frame {i}/{TOTAL}")
    print("encoding with ffmpeg ...")
    cmd = [
        "ffmpeg", "-y", "-framerate", str(FPS),
        "-i", os.path.join(FRAMES, "f%05d.png"),
        "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-profile:v", "high",
        "-crf", "19", "-preset", "medium", "-r", str(FPS),
        "-c:a", "aac", "-b:a", "96k", "-shortest",
        "-movflags", "+faststart", OUT,
    ]
    subprocess.run(cmd, check=True)
    for f in os.listdir(FRAMES):
        os.remove(os.path.join(FRAMES, f))
    os.rmdir(FRAMES)
    print(f"done: {OUT} ({os.path.getsize(OUT)} bytes)")


if __name__ == "__main__":
    sys.exit(main())
