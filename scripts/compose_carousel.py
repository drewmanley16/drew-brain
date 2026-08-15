#!/usr/bin/env python3
"""
Compose a daily IG carousel: a photo cover slide, N video-recommendation
slides, and a photo outro slide. Used by skills/generate-daily-carousel.md.

Usage:
    python3 compose_carousel.py config.json

config.json shape:
{
  "background": "assets/carousel-backgrounds/inbox/1.png",
  "out_dir": "projects/carousels/2026-08-16-docker",
  "cover": {"line1": "best youtube videos", "line2": "to learn docker"},
  "outro": {"line1": "follow for more", "line2": "free resources"},
  "videos": [
    {"screenshot": "/tmp/vid1.png", "rank": 1, "title": "Docker Tutorial for Beginners",
     "channel": "TechWorld with Nana", "note": "full course, start here"}
  ]
}

Canvas is 1080x1350 (4:5, IG's tallest allowed feed ratio).
"""
import json
import sys
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

W, H = 1080, 1350
BRAND_DARK = (14, 14, 16)
BRAND_CARD = (24, 24, 27)
WHITE = (245, 245, 245)
DIM = (170, 170, 175)
ACCENT = (255, 214, 51)  # matches the yellow CTA-card accent used in the video pipeline

FONT_DIR_CANDIDATES = [
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
]


def load_font(size, bold=True):
    candidates = FONT_DIR_CANDIDATES if bold else FONT_DIR_CANDIDATES[1:]
    for path in candidates:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                continue
    return ImageFont.load_default()


def cover_or_crop(img, target_w, target_h):
    return ImageOps.fit(img, (target_w, target_h), method=Image.LANCZOS)


def draw_wrapped(draw, text, font, xy, max_width, fill, line_spacing=1.15, anchor_center=True):
    words = text.split()
    lines, current = [], ""
    for word in words:
        trial = (current + " " + word).strip()
        if draw.textlength(trial, font=font) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)

    x, y = xy
    line_h = font.size * line_spacing
    for line in lines:
        if anchor_center:
            w = draw.textlength(line, font=font)
            draw.text((x - w / 2, y), line, font=font, fill=fill)
        else:
            draw.text((x, y), line, font=font, fill=fill)
        y += line_h
    return y


def make_bookend_slide(bg_path, line1, line2, out_path, tag=None):
    """Cover/outro slide: background photo + dark gradient + bold centered text."""
    bg = Image.open(bg_path).convert("RGB")
    bg = cover_or_crop(bg, W, H)

    gradient = Image.new("L", (1, H), color=0)
    for y in range(H):
        # darker toward the bottom so white text stays readable
        gradient.putpixel((0, y), int(255 * min(1.0, max(0.0, (y - H * 0.35) / (H * 0.65))) * 0.8))
    gradient = gradient.resize((W, H))
    black = Image.new("RGB", (W, H), (0, 0, 0))
    bg = Image.composite(black, bg, gradient)

    draw = ImageDraw.Draw(bg)

    if tag:
        tag_font = load_font(34)
        tw = draw.textlength(tag.upper(), font=tag_font)
        draw.text((W / 2 - tw / 2, 90), tag.upper(), font=tag_font, fill=ACCENT)

    title_font = load_font(78)
    y = H * 0.62
    y = draw_wrapped(draw, line1, title_font, (W / 2, y), W - 140, WHITE)
    if line2:
        y = draw_wrapped(draw, line2, title_font, (W / 2, y + 10), W - 140, WHITE)

    bg.save(out_path)
    return out_path


def make_video_slide(screenshot_path, rank, title, channel, note, out_path, total=None):
    """One recommendation card: dark background, screenshot up top, text below."""
    canvas = Image.new("RGB", (W, H), BRAND_DARK)
    draw = ImageDraw.Draw(canvas)

    pad = 60
    shot_w = W - pad * 2
    shot_h = int(shot_w * 9 / 16)
    shot_top = 150

    if screenshot_path and Path(screenshot_path).exists():
        shot = Image.open(screenshot_path).convert("RGB")
        shot = cover_or_crop(shot, shot_w, shot_h)
        # rounded-corner-ish card via a subtle border
        canvas.paste(shot, (pad, shot_top))
        draw.rectangle([pad, shot_top, pad + shot_w, shot_top + shot_h], outline=(60, 60, 64), width=3)
    else:
        draw.rectangle([pad, shot_top, pad + shot_w, shot_top + shot_h], fill=BRAND_CARD)
        ph_font = load_font(30, bold=False)
        msg = "screenshot missing"
        w = draw.textlength(msg, font=ph_font)
        draw.text((pad + shot_w / 2 - w / 2, shot_top + shot_h / 2 - 15), msg, font=ph_font, fill=DIM)

    rank_font = load_font(56)
    rank_label = f"{rank}/{total}" if total else str(rank)
    draw.text((pad, 60), rank_label, font=rank_font, fill=ACCENT)

    title_font = load_font(52)
    channel_font = load_font(34, bold=False)
    note_font = load_font(32, bold=False)

    y = shot_top + shot_h + 50
    y = draw_wrapped(draw, title, title_font, (W / 2, y), W - 140, WHITE, anchor_center=True)
    y += 10
    cw = draw.textlength(channel.upper(), font=channel_font)
    draw.text((W / 2 - cw / 2, y), channel.upper(), font=channel_font, fill=ACCENT)
    y += 55
    if note:
        draw_wrapped(draw, note, note_font, (W / 2, y), W - 180, DIM, anchor_center=True)

    canvas.save(out_path)
    return out_path


def main():
    if len(sys.argv) != 2:
        print("usage: compose_carousel.py config.json", file=sys.stderr)
        sys.exit(1)

    config = json.loads(Path(sys.argv[1]).read_text())
    out_dir = Path(config["out_dir"])
    out_dir.mkdir(parents=True, exist_ok=True)

    bg = config["background"]
    cover = config["cover"]
    outro = config["outro"]
    videos = config["videos"]

    made = []
    made.append(make_bookend_slide(bg, cover["line1"], cover.get("line2", ""), out_dir / "01-cover.png",
                                    tag=config.get("tag")))

    for i, v in enumerate(videos, start=1):
        out = out_dir / f"{i + 1:02d}-video.png"
        make_video_slide(v.get("screenshot"), v.get("rank", i), v["title"], v["channel"],
                          v.get("note", ""), out, total=len(videos))
        made.append(out)

    last_n = len(videos) + 2
    made.append(make_bookend_slide(bg, outro["line1"], outro.get("line2", ""),
                                    out_dir / f"{last_n:02d}-outro.png", tag=config.get("tag")))

    print(f"wrote {len(made)} slides to {out_dir}")
    for p in made:
        print(f"  {p}")


if __name__ == "__main__":
    main()
