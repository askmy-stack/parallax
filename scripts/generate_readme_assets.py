#!/usr/bin/env python3
"""Generate README animation assets for Reliable Agent Systems."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parents[1] / "docs" / "assets"
BG = (11, 18, 32)
TEAL = (45, 212, 191)
TEAL_DIM = (30, 90, 95)
AMBER = (245, 158, 11)
AMBER_DIM = (120, 80, 20)
WHITE = (226, 232, 240)
MUTED = (148, 163, 184)
PANEL = (17, 28, 48)
PANEL_HI = (24, 42, 68)

STEPS = [
    ("Controlled failure", "Inject labeled degradation"),
    ("Semantic execution trace", "Goals · expectations · observations"),
    ("Early failure detection", "Warn before task collapse"),
    ("Root-cause diagnosis", "Attribute the failure class"),
    ("Risk estimation", "Is continuing still safe?"),
    ("Recovery selection", "Retry · replan · refresh · stop"),
    ("Post-recovery evaluation", "Success · cost · residual risk"),
]


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def rounded(draw: ImageDraw.ImageDraw, xy: tuple[int, int, int, int], fill: tuple[int, ...], radius: int = 18) -> None:
    draw.rounded_rectangle(xy, radius=radius, fill=fill)


def draw_frame(active: int, pulse: float) -> Image.Image:
    w, h = 920, 520
    img = Image.new("RGB", (w, h), BG)
    draw = ImageDraw.Draw(img)

    # subtle grid
    for x in range(0, w, 40):
        draw.line([(x, 0), (x, h)], fill=(18, 28, 48), width=1)
    for y in range(0, h, 40):
        draw.line([(0, y), (w, y)], fill=(18, 28, 48), width=1)

    title = font(28, bold=True)
    subtitle = font(16)
    step_font = font(18, bold=True)
    detail_font = font(13)

    draw.text((40, 28), "RELIABILITY LIFECYCLE", fill=WHITE, font=title)
    draw.text(
        (40, 68),
        "From controlled failure → detection → diagnosis → recovery",
        fill=MUTED,
        font=subtitle,
    )

    # vertical pipeline on left + detail card on right
    left_x = 56
    top = 118
    gap = 48
    node_r = 12

    for i, (label, detail) in enumerate(STEPS):
        y = top + i * gap
        done = i < active
        current = i == active
        color = TEAL if done or current else TEAL_DIM
        if current:
            # pulse ring
            pr = int(node_r + 6 + pulse * 8)
            alpha_ring = AMBER if "fail" in label.lower() or i == 0 else TEAL
            draw.ellipse(
                (left_x - pr, y - pr, left_x + pr, y + pr),
                outline=alpha_ring,
                width=2,
            )
            fill = AMBER if i == 0 else TEAL
        elif done:
            fill = TEAL
        else:
            fill = TEAL_DIM

        draw.ellipse((left_x - node_r, y - node_r, left_x + node_r, y + node_r), fill=fill)
        if i < len(STEPS) - 1:
            y2 = top + (i + 1) * gap
            line_color = TEAL if i < active else TEAL_DIM
            draw.line([(left_x, y + node_r + 2), (left_x, y2 - node_r - 2)], fill=line_color, width=3)

        text_color = WHITE if done or current else MUTED
        draw.text((left_x + 28, y - 11), label, fill=text_color, font=step_font)

    # right detail panel
    panel = (480, 118, 880, 470)
    rounded(draw, panel, PANEL if active % 2 == 0 else PANEL_HI, radius=22)
    draw.rounded_rectangle(panel, radius=22, outline=TEAL if active > 0 else AMBER, width=2)

    label, detail = STEPS[active]
    badge = "ACTIVE STAGE"
    draw.text((510, 150), badge, fill=AMBER if active == 0 else TEAL, font=detail_font)
    draw.text((510, 180), label, fill=WHITE, font=font(26, bold=True))
    draw.text((510, 230), detail, fill=MUTED, font=subtitle)

    # mini expected vs observed bars
    draw.text((510, 290), "Signal view", fill=MUTED, font=detail_font)
    # expectation bar
    draw.text((510, 320), "Expectation", fill=TEAL, font=detail_font)
    draw.rounded_rectangle((510, 342, 850, 358), radius=6, fill=TEAL_DIM)
    draw.rounded_rectangle((510, 342, 510 + int(340 * 0.82), 358), radius=6, fill=TEAL)
    # observation bar (diverges after stage 1)
    draw.text((510, 378), "Observation", fill=AMBER, font=detail_font)
    obs = 0.82 if active < 2 else max(0.35, 0.82 - (active - 1) * 0.08)
    if active >= 5:
        obs = 0.8  # recovery realigns
    draw.rounded_rectangle((510, 400, 850, 416), radius=6, fill=AMBER_DIM)
    draw.rounded_rectangle((510, 400, 510 + int(340 * obs), 416), radius=6, fill=AMBER)

    gap_text = "aligned" if abs(0.82 - obs) < 0.05 else "divergence detected"
    draw.text((510, 436), f"Expected–observed gap: {gap_text}", fill=MUTED, font=detail_font)

    draw.text((40, 488), "Parallax  ·  AgentFailBench × Semantic Monitor × RecoverAI", fill=MUTED, font=detail_font)
    return img


def make_lifecycle_gif() -> Path:
    frames: list[Image.Image] = []
    for active in range(len(STEPS)):
        for pulse_i in range(4):
            frames.append(draw_frame(active, pulse_i / 3))
    # hold final
    frames.extend([draw_frame(len(STEPS) - 1, 1.0)] * 6)

    out = OUT / "reliability-lifecycle.gif"
    frames[0].save(
        out,
        save_all=True,
        append_images=frames[1:],
        duration=180,
        loop=0,
        optimize=True,
    )
    return out


def make_drift_gif() -> Path:
    """Compact expected-vs-observed divergence loop."""
    w, h = 720, 300
    frames: list[Image.Image] = []
    title = font(22, bold=True)
    body = font(14)
    for t in range(28):
        img = Image.new("RGB", (w, h), BG)
        draw = ImageDraw.Draw(img)
        for x in range(0, w, 36):
            draw.line([(x, 0), (x, h)], fill=(18, 28, 48), width=1)
        draw.text((28, 22), "EXPECTED  ×  OBSERVED", fill=WHITE, font=title)
        draw.text((28, 54), "Semantic drift without exceptions  ·  HTTP 200 still passes", fill=MUTED, font=body)

        pts_exp: list[tuple[int, int]] = []
        pts_obs: list[tuple[int, int]] = []
        drift_scale = min(1.0, t / 18)
        for x in range(48, 680, 3):
            progress = (x - 48) / 632
            y_exp = 155 - int(55 * progress)
            drift = 0
            if progress > 0.32:
                drift = int(95 * min(1.0, (progress - 0.32) / 0.45) * drift_scale)
            pts_exp.append((x, y_exp))
            pts_obs.append((x, y_exp + drift))

        # dashed expectation (draw short segments)
        for i in range(0, len(pts_exp) - 1, 2):
            draw.line([pts_exp[i], pts_exp[min(i + 1, len(pts_exp) - 1)]], fill=TEAL, width=3)
        draw.line(pts_obs, fill=AMBER, width=3)

        draw.ellipse((pts_exp[0][0] - 6, pts_exp[0][1] - 6, pts_exp[0][0] + 6, pts_exp[0][1] + 6), fill=TEAL)
        draw.ellipse((pts_exp[-1][0] - 5, pts_exp[-1][1] - 5, pts_exp[-1][0] + 5, pts_exp[-1][1] + 5), outline=TEAL, width=2)
        if drift_scale > 0.25:
            idx = int(0.55 * (len(pts_obs) - 1))
            draw.ellipse(
                (pts_obs[idx][0] - 8, pts_obs[idx][1] - 8, pts_obs[idx][0] + 8, pts_obs[idx][1] + 8),
                fill=AMBER,
            )
            draw.text((pts_obs[idx][0] + 14, pts_obs[idx][1] - 10), "drift detected", fill=AMBER, font=body)

        # legend swatches
        draw.rounded_rectangle((28, 250, 48, 262), radius=3, fill=TEAL)
        draw.text((56, 246), "expectation (dashed)", fill=TEAL, font=body)
        draw.rounded_rectangle((260, 250, 280, 262), radius=3, fill=AMBER)
        draw.text((288, 246), "observation", fill=AMBER, font=body)
        frames.append(img)

    frames = frames + frames[-2:0:-1]
    out = OUT / "semantic-drift.gif"
    frames[0].save(
        out,
        save_all=True,
        append_images=frames[1:],
        duration=65,
        loop=0,
        optimize=True,
    )
    return out


def optimize_pngs() -> None:
    for path in OUT.glob("*.png"):
        im = Image.open(path).convert("RGB")
        # README-friendly width
        max_w = 1280
        if im.width > max_w:
            ratio = max_w / im.width
            im = im.resize((max_w, int(im.height * ratio)), Image.Resampling.LANCZOS)
        im.save(path, format="PNG", optimize=True)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    optimize_pngs()
    life = make_lifecycle_gif()
    drift = make_drift_gif()
    print(life, life.stat().st_size)
    print(drift, drift.stat().st_size)
