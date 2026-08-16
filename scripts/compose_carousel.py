#!/usr/bin/env python3
"""
Compose a daily IG carousel matching the drewisliving template: a photo
cover slide (title + subtitle pill, optional proof-graphic), one card per
featured YouTube video (title pill + real screenshot + description), and
a photo outro slide (optional profile-card screenshot + CTA pill).
Used by skills/generate-daily-carousel.md.

Usage:
    python3 compose_carousel.py config.json

config.json shape:
{
  "background": "assets/carousel-backgrounds/inbox/1.png",
  "out_dir": "projects/carousels/2026-08-16-docker",
  "cover": {
    "title_lines": [
      [{"text": "5 Coding Projects", "underline": true}, {"text": "you"}],
      [{"text": "can build"}, {"text": "this week", "color": "accent"}]
    ],
    "subtitle": [{"text": "to actually look good on a resume", "color": "accent", "from": 3}],
    "proof_graphic": "assets/carousel-brand/github-graph.png",
    "proof_logo": "assets/carousel-brand/github-logo.png",
    "tag_text": "w/YouTube Tutorials"
  },
  "outro": {
    "profile_card": "assets/carousel-brand/ig-profile-card.png",
    "lines": ["Want all 5 tutorials?", "Follow + comment"],
    "cta_word": "Project"
  },
  "videos": [
    {"rank": 1, "title": "Build Your Own AI Agent", "screenshot": "/tmp/vid1.png",
     "description": "Build an AI research agent in Python that can use different LLMs, call external tools, search for information, and return structured results."}
  ]
}

Canvas is 1080x1350 (4:5, IG's tallest allowed feed ratio). All text
segments default to white; set "color": "accent" for the yellow highlight
color. Segments support "underline": true.
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

W, H = 1080, 1350
WHITE = (245, 245, 245)
DIM = (210, 210, 215)
ACCENT = (255, 214, 61)
PILL = (26, 26, 30, 235)
DUOTONE = (18, 28, 46)  # navy tint multiplied over background photos

BOLD_ROUNDED = "/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf"
SERIF_BOLD = "/System/Library/Fonts/Supplemental/Georgia Bold.ttf"
PLAIN = "/System/Library/Fonts/Supplemental/Arial.ttf"


def font(size, kind="rounded"):
    path = {"rounded": BOLD_ROUNDED, "serif": SERIF_BOLD, "plain": PLAIN}[kind]
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def cover_crop(img, w, h):
    return ImageOps.fit(img, (w, h), method=Image.LANCZOS)


def duotone_bg(bg_path):
    bg = Image.open(bg_path).convert("RGB")
    bg = cover_crop(bg, W, H)
    tint = Image.new("RGB", (W, H), DUOTONE)
    return Image.blend(bg, tint, 0.42)


def color_of(seg):
    return ACCENT if seg.get("color") == "accent" else WHITE


def segment_lines(draw, lines, f, max_width):
    """Wrap a list of pre-grouped lines (each a list of segments) so any
    single line wider than max_width gets pushed onto the next line as a
    whole segment. Keeps day-to-day text authoring simple (segments map
    1:1 to a visual line) while still guarding against overflow."""
    out = []
    for line in lines:
        text = " ".join(s["text"] for s in line)
        if draw.textlength(text, font=f) <= max_width or len(line) == 1:
            out.append(line)
        else:
            mid = len(line) // 2
            out.append(line[:mid])
            out.append(line[mid:])
    return out


def draw_segment_line(draw, segments, f, center_x, y, space=14):
    total_w = sum(draw.textlength(s["text"], font=f) for s in segments)
    total_w += space * (len(segments) - 1)
    x = center_x - total_w / 2
    for s in segments:
        w = draw.textlength(s["text"], font=f)
        draw.text((x, y), s["text"], font=f, fill=color_of(s))
        if s.get("underline"):
            draw.line([(x, y + f.size + 4), (x + w, y + f.size + 4)], fill=color_of(s), width=5)
        x += w + space
    return y + f.size * 1.2


def rounded_pill(canvas, xy, size, radius=34, fill=PILL):
    x, y = xy
    w, h = size
    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    ImageDraw.Draw(overlay).rounded_rectangle([x, y, x + w, y + h], radius=radius, fill=fill)
    canvas.alpha_composite(overlay)


def measure_wrapped(draw, text, f, max_width):
    words = text.split()
    lines, current = [], ""
    for word in words:
        trial = (current + " " + word).strip()
        if draw.textlength(trial, font=f) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_wrapped_centered(draw, text, f, center_x, y, max_width, fill, line_spacing=1.25):
    for line in measure_wrapped(draw, text, f, max_width):
        w = draw.textlength(line, font=f)
        draw.text((center_x - w / 2, y), line, font=f, fill=fill)
        y += f.size * line_spacing
    return y


def make_cover(config, out_path):
    cover = config["cover"]
    canvas = duotone_bg(config["background"]).convert("RGBA")
    draw = ImageDraw.Draw(canvas)

    title_font = font(70)
    y = 190
    lines = segment_lines(draw, cover["title_lines"], title_font, W - 120)
    for line in lines:
        y = draw_segment_line(draw, line, title_font, W / 2, y)
        y += 16

    if cover.get("subtitle"):
        sub_font = font(34)
        sub_text = " ".join(s["text"] for s in cover["subtitle"])
        pad_x, pad_y = 40, 22
        text_w = sum(draw.textlength(s["text"], font=sub_font) for s in cover["subtitle"])
        text_w += 14 * (len(cover["subtitle"]) - 1)
        pill_w, pill_h = text_w + pad_x * 2, sub_font.size + pad_y * 2
        pill_x = W / 2 - pill_w / 2
        rounded_pill(canvas, (pill_x, y + 20), (pill_w, pill_h))
        draw = ImageDraw.Draw(canvas)
        draw_segment_line(draw, cover["subtitle"], sub_font, W / 2, y + 20 + pad_y - 6)
        y += 20 + pill_h + 30

    if cover.get("proof_graphic") and Path(cover["proof_graphic"]).exists():
        graphic = Image.open(cover["proof_graphic"]).convert("RGBA")
        gw = W - 100
        gh = int(gw * graphic.height / graphic.width)
        graphic = graphic.resize((gw, gh), Image.LANCZOS)
        canvas.alpha_composite(graphic, (50, int(y)))
        y += gh + 40

    if cover.get("proof_logo") and Path(cover["proof_logo"]).exists():
        logo = Image.open(cover["proof_logo"]).convert("RGBA")
        ls = 150
        logo = logo.resize((ls, ls), Image.LANCZOS)
        canvas.alpha_composite(logo, (50, int(y)))

    if cover.get("tag_text"):
        tag_font = font(52, kind="serif")
        draw = ImageDraw.Draw(canvas)
        draw.text((240, int(y) + 45), cover["tag_text"], font=tag_font, fill=WHITE,
                   stroke_width=1, stroke_fill=(80, 80, 80))

    canvas.convert("RGB").save(out_path)


def make_video_slide(video, index, total, out_path):
    canvas = Image.new("RGBA", (W, H), (14, 14, 16, 255))
    draw = ImageDraw.Draw(canvas)

    pill_font = font(54)
    label = f"{video.get('rank', index)}) {video['title']}"
    pad_x, pad_y = 34, 24
    max_pill_w = W - 120
    lines = measure_wrapped(draw, label, pill_font, max_pill_w - pad_x * 2)
    line_h = pill_font.size * 1.15
    pill_w = max(draw.textlength(line, font=pill_font) for line in lines) + pad_x * 2
    pill_h = line_h * len(lines) + pad_y * 2
    rounded_pill(canvas, (70, 60), (pill_w, pill_h))
    draw = ImageDraw.Draw(canvas)
    ty = 60 + pad_y
    for line in lines:
        draw.text((70 + pad_x, ty), line, font=pill_font, fill=WHITE)
        ty += line_h

    shot_top = 60 + pill_h + 50
    pad = 60
    shot_w = W - pad * 2
    shot_h = int(shot_w * 9 / 16)
    screenshot = video.get("screenshot")
    if screenshot and Path(screenshot).exists():
        shot = Image.open(screenshot).convert("RGB")
        shot = cover_crop(shot, shot_w, shot_h)
        canvas.paste(shot, (pad, int(shot_top)))
    else:
        draw.rectangle([pad, shot_top, pad + shot_w, shot_top + shot_h], fill=(30, 30, 34))
        msg_font = font(30, kind="plain")
        msg = "screenshot missing"
        w = draw.textlength(msg, font=msg_font)
        draw.text((pad + shot_w / 2 - w / 2, shot_top + shot_h / 2 - 15), msg, font=msg_font, fill=DIM)
    draw.rectangle([pad, shot_top, pad + shot_w, shot_top + shot_h], outline=(50, 50, 54), width=2)

    desc_font = font(44)
    desc_y = shot_top + shot_h + 60
    draw_wrapped_centered(draw, video["description"], desc_font, W / 2, desc_y, W - 140, WHITE)

    canvas.convert("RGB").save(out_path)


def make_outro(config, out_path):
    outro = config["outro"]
    canvas = duotone_bg(config["background"]).convert("RGBA")
    draw = ImageDraw.Draw(canvas)

    y = 150
    if outro.get("profile_card") and Path(outro["profile_card"]).exists():
        card = Image.open(outro["profile_card"]).convert("RGBA")
        cw = W - 260
        ch = int(cw * card.height / card.width)
        card = card.resize((cw, ch), Image.LANCZOS)
        canvas.alpha_composite(card, (90, y))
        y += ch + 90

    body_font = font(56)
    all_lines = list(outro["lines"])
    quoted = f'"{outro["cta_word"]}"'
    pad_x, pad_y = 45, 40
    max_w = max(draw.textlength(l, font=body_font) for l in all_lines)
    max_w = max(max_w, draw.textlength(quoted, font=body_font))
    pill_w = max_w + pad_x * 2
    pill_h = pad_y * 2 + body_font.size * 1.3 * (len(all_lines) + 1)
    pill_x = 90
    rounded_pill(canvas, (pill_x, y), (pill_w, pill_h))
    draw = ImageDraw.Draw(canvas)
    ty = y + pad_y
    center_x = pill_x + pill_w / 2
    for line in all_lines:
        w = draw.textlength(line, font=body_font)
        draw.text((center_x - w / 2, ty), line, font=body_font, fill=WHITE)
        ty += body_font.size * 1.3
    prefix = '"'
    word = outro["cta_word"]
    suffix = '"'
    seg_w = draw.textlength(prefix + word + suffix, font=body_font)
    x = center_x - seg_w / 2
    draw.text((x, ty), prefix, font=body_font, fill=WHITE)
    x += draw.textlength(prefix, font=body_font)
    draw.text((x, ty), word, font=body_font, fill=ACCENT)
    x += draw.textlength(word, font=body_font)
    draw.text((x, ty), suffix, font=body_font, fill=WHITE)

    canvas.convert("RGB").save(out_path)


def main():
    if len(sys.argv) != 2:
        print("usage: compose_carousel.py config.json", file=sys.stderr)
        sys.exit(1)

    config = json.loads(Path(sys.argv[1]).read_text())
    out_dir = Path(config["out_dir"])
    out_dir.mkdir(parents=True, exist_ok=True)

    made = []
    cover_path = out_dir / "01-cover.png"
    make_cover(config, cover_path)
    made.append(cover_path)

    videos = config["videos"]
    for i, v in enumerate(videos, start=1):
        out = out_dir / f"{i + 1:02d}-video.png"
        make_video_slide(v, i, len(videos), out)
        made.append(out)

    outro_path = out_dir / f"{len(videos) + 2:02d}-outro.png"
    make_outro(config, outro_path)
    made.append(outro_path)

    print(f"wrote {len(made)} slides to {out_dir}")
    for p in made:
        print(f"  {p}")


if __name__ == "__main__":
    main()
