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
  "backgrounds": [
    "assets/carousel-backgrounds/inbox/1.png",
    "assets/carousel-backgrounds/inbox/2.png",
    "assets/carousel-backgrounds/inbox/3.png"
  ],
  "out_dir": "projects/carousels/2026-08-16-docker",
  "cover": {
    "title_lines": [
      [{"text": "5 Coding Projects", "underline": true}, {"text": "you"}],
      [{"text": "can build"}, {"text": "this week", "color": "accent"}]
    ],
    "subtitle": [{"text": "to actually look good on a resume", "color": "accent", "from": 3}],
    "proof_graphic": "assets/carousel-brand/github-graph.png",
    "proof_logo": "assets/carousel-brand/github-logo.png",
    "tag_icon": "assets/carousel-brand/youtube-icon.png",
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

"backgrounds" needs exactly one photo per slide (cover + one per video +
outro) -- every slide gets its own duotone-tinted background photo, matching
the reference template where each card in the carousel uses a different
shot. If omitted, falls back to a single top-level "background" repeated on
every slide.
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

HELVETICA_NEUE = "/System/Library/Fonts/HelveticaNeue.ttc"
SERIF_BOLD = "/System/Library/Fonts/Supplemental/Georgia Bold.ttf"
PLAIN = "/System/Library/Fonts/Supplemental/Arial.ttf"


def font(size, kind="rounded"):
    if kind == "rounded":
        try:
            return ImageFont.truetype(HELVETICA_NEUE, size, index=1)  # Helvetica Neue Bold
        except OSError:
            pass
    path = {"serif": SERIF_BOLD, "plain": PLAIN}.get(kind, PLAIN)
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


def draw_wrapped_centered(draw, text, f, center_x, y, max_width, fill, line_spacing=1.25,
                           stroke_width=0, stroke_fill=None):
    for line in measure_wrapped(draw, text, f, max_width):
        w = draw.textlength(line, font=f)
        draw.text((center_x - w / 2, y), line, font=f, fill=fill,
                   stroke_width=stroke_width, stroke_fill=stroke_fill)
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
        card = Image.new("RGBA", (gw + 30, gh + 30), (255, 255, 255, 255))
        card.alpha_composite(graphic, (15, 15))
        canvas.alpha_composite(card, (50 - 15, int(y)))
        y += gh + 30 + 40

    row_x = 50
    if cover.get("proof_logo") and Path(cover["proof_logo"]).exists():
        logo = Image.open(cover["proof_logo"]).convert("RGBA")
        ls = 140
        logo = logo.resize((ls, ls), Image.LANCZOS)
        canvas.alpha_composite(logo, (row_x, int(y)))
        row_x += ls + 40

    if cover.get("tag_icon") and Path(cover["tag_icon"]).exists():
        icon = Image.open(cover["tag_icon"]).convert("RGBA")
        isz = 90
        icon = ImageOps.contain(icon, (isz, isz))
        canvas.alpha_composite(icon, (row_x, int(y) + 25))
        row_x += isz + 24

    if cover.get("tag_text"):
        tag_font = font(52, kind="serif")
        draw = ImageDraw.Draw(canvas)
        draw.text((row_x, int(y) + 45), cover["tag_text"], font=tag_font, fill=WHITE,
                   stroke_width=1, stroke_fill=(80, 80, 80))

    canvas.convert("RGB").save(out_path)


def make_video_slide(video, index, total, background, out_path):
    canvas = duotone_bg(background).convert("RGBA")
    draw = ImageDraw.Draw(canvas)

    title_font = font(58)
    label = f"{video.get('rank', index)}) {video['title']}"
    title_lines = measure_wrapped(draw, label, title_font, W - 140)
    title_line_h = title_font.size * 1.2
    title_h = title_line_h * len(title_lines)

    shot_w = int((W - 200) * 0.85)
    shot_h = int(shot_w * 9 / 16)
    shot_x = (W - shot_w) // 2

    desc_font = font(44)
    desc_lines = measure_wrapped(draw, video["description"], desc_font, W - 160)
    desc_line_h = desc_font.size * 1.25
    desc_h = desc_line_h * len(desc_lines)

    gap1, gap2 = 55, 55
    total_h = title_h + gap1 + shot_h + gap2 + desc_h
    y = (H - total_h) / 2

    y = draw_wrapped_centered(draw, label, title_font, W / 2, y, W - 140, WHITE,
                               line_spacing=1.2, stroke_width=3, stroke_fill=(0, 0, 0))
    y += gap1 - (title_line_h - title_font.size)

    screenshot = video.get("screenshot")
    if screenshot and Path(screenshot).exists():
        shot = Image.open(screenshot).convert("RGB")
        shot = cover_crop(shot, shot_w, shot_h)
        canvas.paste(shot, (shot_x, int(y)))
    else:
        draw.rectangle([shot_x, y, shot_x + shot_w, y + shot_h], fill=(30, 30, 34))
        msg_font = font(30, kind="plain")
        msg = "screenshot missing"
        w = draw.textlength(msg, font=msg_font)
        draw.text((W / 2 - w / 2, y + shot_h / 2 - 15), msg, font=msg_font, fill=DIM)
    y += shot_h + gap2

    draw_wrapped_centered(draw, video["description"], desc_font, W / 2, y, W - 160, WHITE,
                           line_spacing=1.25, stroke_width=2, stroke_fill=(0, 0, 0))

    canvas.convert("RGB").save(out_path)


def make_outro(config, out_path):
    outro = config["outro"]
    canvas = duotone_bg(config["background"]).convert("RGBA")
    draw = ImageDraw.Draw(canvas)

    y = 110
    if outro.get("profile_card") and Path(outro["profile_card"]).exists():
        card = Image.open(outro["profile_card"]).convert("RGBA")
        cw = int((W - 160) * 0.9)
        ch = int(cw * card.height / card.width)
        card = card.resize((cw, ch), Image.LANCZOS)
        # soften hard rectangular edges of the raw screenshot against the photo
        mask = Image.new("L", card.size, 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, cw, ch], radius=28, fill=255)
        canvas.alpha_composite(Image.composite(card, Image.new("RGBA", card.size, (0, 0, 0, 0)), mask),
                                ((W - cw) // 2, y))
        y += ch + 70

    body_font = font(56)
    all_lines = list(outro["lines"])
    line_h = body_font.size * 1.3
    for line in all_lines:
        w = draw.textlength(line, font=body_font)
        draw.text((W / 2 - w / 2, y), line, font=body_font, fill=WHITE,
                   stroke_width=3, stroke_fill=(0, 0, 0))
        y += line_h

    prefix, word, suffix = '"', outro["cta_word"], '"'
    seg_w = draw.textlength(prefix + word + suffix, font=body_font)
    x = W / 2 - seg_w / 2
    draw.text((x, y), prefix, font=body_font, fill=WHITE, stroke_width=3, stroke_fill=(0, 0, 0))
    x += draw.textlength(prefix, font=body_font)
    draw.text((x, y), word, font=body_font, fill=ACCENT, stroke_width=3, stroke_fill=(0, 0, 0))
    x += draw.textlength(word, font=body_font)
    draw.text((x, y), suffix, font=body_font, fill=WHITE, stroke_width=3, stroke_fill=(0, 0, 0))

    canvas.convert("RGB").save(out_path)


def main():
    if len(sys.argv) != 2:
        print("usage: compose_carousel.py config.json", file=sys.stderr)
        sys.exit(1)

    config = json.loads(Path(sys.argv[1]).read_text())
    base_out_dir = Path(config["out_dir"])

    videos = config["videos"]
    backgrounds = config.get("backgrounds")
    if not backgrounds:
        # fall back to cycling a single background through every slide
        single = config["background"]
        backgrounds = [single] * (len(videos) + 2)
    assert len(backgrounds) == len(videos) + 2, (
        f"backgrounds must have one entry per slide (cover + {len(videos)} videos + outro "
        f"= {len(videos) + 2}), got {len(backgrounds)}"
    )

    # always produce two sibling sets: "with-thumbnails" (real screenshots, if
    # given) and "placeholder" (thumbnails stripped) so Drew has a blank set
    # ready to hand-fill if a screenshot is missing/wrong/needs swapping.
    variants = {
        "with-thumbnails": videos,
        "placeholder": [dict(v, screenshot=None) for v in videos],
    }

    for variant_name, variant_videos in variants.items():
        out_dir = base_out_dir / variant_name
        out_dir.mkdir(parents=True, exist_ok=True)
        made = build_carousel(config, variant_videos, backgrounds, out_dir)
        print(f"wrote {len(made)} slides to {out_dir}")
        for p in made:
            print(f"  {p}")


def build_carousel(config, videos, backgrounds, out_dir):
    made = []
    cover_config = dict(config, background=backgrounds[0])
    cover_path = out_dir / "01-cover.png"
    make_cover(cover_config, cover_path)
    made.append(cover_path)

    for i, v in enumerate(videos, start=1):
        out = out_dir / f"{i + 1:02d}-video.png"
        make_video_slide(v, i, len(videos), backgrounds[i], out)
        made.append(out)

    # the outro always uses the same fixed signature photo (not the rotating
    # inbox pool) so every post ends on the same recognizable shot -- swap
    # assets/carousel-brand/outro-photo.png to change it everywhere at once
    signature_photo = Path("assets/carousel-brand/outro-photo.png")
    outro_bg = str(signature_photo) if signature_photo.exists() else backgrounds[-1]
    outro_config = dict(config, background=outro_bg)
    outro_path = out_dir / f"{len(videos) + 2:02d}-outro.png"
    make_outro(outro_config, outro_path)
    made.append(outro_path)
    return made


if __name__ == "__main__":
    main()
