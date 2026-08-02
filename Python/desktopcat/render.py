"""Procedural drawing of the cat with QPainter. No sprite assets (Phase 0),
mood-driven pose (Phase 1). Every function is a plain function taking a
QPainter and the state dict -- no classes.
"""

import math

from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import QBrush, QColor, QPainter, QPainterPath, QPen, QRegion
from PySide6.QtWidgets import QWidget


OUTLINE = QColor(70, 45, 30)
FUR = QColor(242, 166, 90)
FUR_DARK = QColor(214, 133, 63)
FUR_HOT = QColor(214, 62, 48)  # Phase 3: overheat red tint target
PUPPY_FUR = QColor(196, 148, 96)  # default puppy fur, used when no custom color is set
BELLY = QColor(255, 231, 199)
PINK = QColor(255, 168, 178)
NOSE_DARK = QColor(55, 42, 40)  # puppy nose (cat's is PINK)
EYE_WHITE = QColor(255, 255, 255)
EYE_PUPIL = QColor(35, 25, 20)
STEAM = QColor(235, 235, 240)
PAPER = QColor(250, 240, 210)
PAPER_ROLL = QColor(228, 210, 172)
PAPER_LINE = QColor(184, 152, 104)

NO_PEN = QPen(Qt.PenStyle.NoPen)


def _round_pen(color, width):
    pen = QPen(color, width)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    return pen


def _tint(base, target, t):
    t = max(0.0, min(1.0, t))
    return QColor(
        int(base.red() + (target.red() - base.red()) * t),
        int(base.green() + (target.green() - base.green()) * t),
        int(base.blue() + (target.blue() - base.blue()) * t),
    )


FIT_SCALE = 0.8  # shrinks the whole cat so ears/tail/paws stay inside the
# canvas with margin -- at 1.0 the ears clip flat against the top edge and
# the mask (below) has to cut into the tail to avoid covering empty space.


def build_click_mask_region(size):
    """A generous rounded-rect covering the whole silhouette (ears/tail
    reach close to the edges at FIT_SCALE) so clicks in the true empty
    corners fall through, without clipping any part of the cat itself.
    A tight ellipse used to sit here and cut into both."""
    margin = int(size * 0.02)
    path = QPainterPath()
    path.addRoundedRect(QRectF(margin, margin, size - margin * 2, size - margin * 2), size * 0.16, size * 0.16)
    return QRegion(path.toFillPolygon().toPolygon())


def paint(widget: QWidget, state: dict, now: float):
    width, height = widget.width(), widget.height()
    pivot_x, pivot_y = width / 2, height * 0.85  # base_y in draw_cat -- feet stay put

    painter = QPainter(widget)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

    painter.save()
    painter.translate(pivot_x, pivot_y)
    painter.rotate(math.degrees(state["wobble_angle"]))
    stretch = state["stretch"]
    painter.scale(FIT_SCALE * (1.0 - stretch * 0.6), FIT_SCALE * (1.0 + stretch))
    painter.translate(-pivot_x, -pivot_y)

    draw_pet(painter, state, width, height, now)
    painter.restore()
    painter.end()


def draw_pet(painter, state, width, height, now):
    """Dispatches between the cat and puppy silhouettes (Phase 6+: pick
    your companion). Body/paws/face/accessories are shared; only
    ears/tail/snout differ enough to actually read as one species or the
    other."""
    pose = state["pose"]
    cx = width / 2
    base_y = height * 0.85
    config = state["config"]
    character = (config.get("character") if config else None) or "cat"
    is_puppy = character == "puppy"

    custom_fur = config.get("fur_color") if config else None
    default_fur = PUPPY_FUR if is_puppy else FUR
    base_fur = QColor(*custom_fur) if custom_fur else default_fur
    fur_color = _tint(base_fur, FUR_HOT, state["heat"])

    body_h = height * 0.42 * (1.0 - 0.35 * pose["crouch"])
    body_w = width * 0.62 * (1.0 + 0.12 * pose["crouch"])
    body_top = base_y - body_h

    if is_puppy:
        _draw_puppy_tail(painter, cx, base_y, body_w, now, state["mood"], fur_color)
    else:
        _draw_tail(painter, cx, base_y, body_w, now, state["mood"], fur_color)
    _draw_body(painter, cx, base_y, body_w, body_h, fur_color)

    envelope = state["knead_envelope"]
    phase = state["knead_phase"]
    knead_l = max(0.0, math.sin(phase)) * envelope
    knead_r = max(0.0, math.sin(phase + math.pi)) * envelope
    _draw_paws(painter, cx, base_y, body_w, pose["paws_forward"], knead_l, knead_r)
    _draw_scroll(painter, cx, base_y, body_w, state["scroll_unroll"])

    head_r = width * 0.30
    head_cy = body_top - head_r * 0.55

    if is_puppy:
        _draw_puppy_ears(painter, cx, head_cy, head_r, pose["ear_flatten"], fur_color)
        _draw_head(painter, cx, head_cy, head_r, fur_color)
        _draw_puppy_snout(painter, cx, head_cy, head_r, fur_color)
    else:
        _draw_ears(painter, cx, head_cy, head_r, pose["ear_flatten"], fur_color)
        _draw_head(painter, cx, head_cy, head_r, fur_color)

    if config and config.get("pattern") == "tabby":
        stripe_color = _tint(base_fur, QColor(0, 0, 0), 0.35)
        _draw_stripes(painter, cx, base_y, body_w, body_h, head_cy, head_r, stripe_color)

    nose_color = NOSE_DARK if is_puppy else PINK
    _draw_face(painter, state, cx, head_cy, head_r, now, nose_color)
    _draw_steam_particles(painter, state["steam_particles"], cx, head_cy - head_r * 1.05)
    if state.get("ai_active"):
        _draw_thinking_dots(painter, cx, head_cy - head_r * 1.3, now)


def _draw_body(painter, cx, base_y, w, h, fur_color):
    path = QPainterPath()
    rect = QRectF(cx - w / 2, base_y - h, w, h)
    path.addRoundedRect(rect, w * 0.35, h * 0.35)
    painter.setPen(NO_PEN)
    painter.setBrush(QBrush(fur_color))
    painter.drawPath(path)

    belly = QRectF(cx - w * 0.22, base_y - h * 0.55, w * 0.44, h * 0.55)
    painter.setPen(NO_PEN)
    painter.setBrush(QBrush(BELLY))
    painter.drawEllipse(belly)


def _draw_paws(painter, cx, base_y, body_w, forward, knead_l, knead_r):
    paw_w, paw_h = body_w * 0.22, body_w * 0.16
    offset_x = body_w * 0.20
    lift_y = forward * body_w * 0.28
    knead_amount = body_w * 0.10

    painter.setPen(NO_PEN)
    painter.setBrush(QBrush(BELLY))
    for side, knead in ((-1, knead_l), (1, knead_r)):
        px = cx + side * offset_x
        py = base_y - paw_h / 2 + lift_y * 0.2 - knead * knead_amount
        rect = QRectF(px - paw_w / 2, py - paw_h / 2 - forward * 6, paw_w, paw_h)
        painter.drawEllipse(rect)


def _draw_scroll(painter, cx, base_y, body_w, unroll):
    """Phase 4: a small paper scroll beside the cat that unspools while
    scrolling and re-rolls once scrolling stops."""
    root_x = cx - body_w * 0.45
    root_y = base_y - body_w * 0.12
    roll_r = body_w * 0.09
    unroll_len = unroll * body_w * 0.25

    if unroll_len > 0.5:
        strip = QRectF(root_x - unroll_len, root_y - roll_r, unroll_len, roll_r * 2)
        painter.setPen(QPen(OUTLINE, 1.5))
        painter.setBrush(QBrush(PAPER))
        painter.drawRoundedRect(strip, roll_r * 0.4, roll_r * 0.4)

        painter.setPen(QPen(PAPER_LINE, 1))
        for frac in (0.35, 0.65):
            line_y = strip.top() + strip.height() * frac
            painter.drawLine(
                QPointF(strip.left() + roll_r * 0.3, line_y),
                QPointF(strip.right() - roll_r * 0.3, line_y),
            )

    painter.setPen(QPen(OUTLINE, 1.5))
    painter.setBrush(QBrush(PAPER_ROLL))
    painter.drawEllipse(QPointF(root_x, root_y), roll_r, roll_r * 1.3)


def _draw_ears(painter, cx, head_cy, r, flatten, fur_color):
    ear_size = r * 0.65
    painter.setPen(NO_PEN)
    painter.setBrush(QBrush(fur_color))
    for side in (-1, 1):
        base_x = cx + side * r * 0.62
        base_y = head_cy - r * 0.55
        tip_dx = side * ear_size * (0.55 + flatten * 0.6)
        tip_dy = -ear_size * (1.0 - flatten * 0.75)

        path = QPainterPath()
        path.moveTo(base_x - side * ear_size * 0.35, base_y + ear_size * 0.25)
        path.lineTo(base_x + tip_dx, base_y + tip_dy)
        path.lineTo(base_x + side * ear_size * 0.35, base_y + ear_size * 0.25)
        path.closeSubpath()
        painter.drawPath(path)

        inner = QPainterPath()
        cx2, cy2 = base_x, base_y + ear_size * 0.08
        inner.moveTo(cx2 - side * ear_size * 0.16, cy2 + ear_size * 0.12)
        inner.lineTo(cx2 + tip_dx * 0.6, cy2 + tip_dy * 0.6)
        inner.lineTo(cx2 + side * ear_size * 0.16, cy2 + ear_size * 0.12)
        inner.closeSubpath()
        painter.setBrush(QBrush(PINK))
        painter.drawPath(inner)
        painter.setBrush(QBrush(fur_color))


def _draw_puppy_ears(painter, cx, head_cy, r, flatten, fur_color):
    """Floppy hanging ears, angled outward -- the single biggest visual
    cue that reads as "dog" rather than "cat". flatten (from the same
    hunt/pounce pose system as the cat's ears) makes them swing back a
    little further instead of pinning flat."""
    ear_w = r * 0.40
    ear_h = r * 0.9 * (1.0 - flatten * 0.2)
    painter.setPen(NO_PEN)
    painter.setBrush(QBrush(fur_color))
    for side in (-1, 1):
        ex = cx + side * r * 0.90
        ey = head_cy + r * 0.05
        painter.save()
        painter.translate(ex, ey)
        painter.rotate(side * (14 + flatten * 10))
        painter.drawEllipse(QPointF(0, ear_h * 0.35), ear_w / 2, ear_h / 2)
        painter.restore()


def _draw_puppy_snout(painter, cx, head_cy, r, fur_color):
    """A small forward-projecting muzzle bump, layered over the shared
    head/muzzle-patch -- cats have a flat face, dogs have a snout."""
    snout_w, snout_h = r * 0.62, r * 0.46
    snout_cy = head_cy + r * 0.40
    painter.setPen(NO_PEN)
    painter.setBrush(QBrush(fur_color))
    painter.drawEllipse(QPointF(cx, snout_cy), snout_w / 2, snout_h / 2)

    patch = QRectF(cx - snout_w * 0.34, snout_cy - snout_h * 0.20, snout_w * 0.68, snout_h * 0.62)
    painter.setBrush(QBrush(BELLY))
    painter.drawEllipse(patch)


def _draw_head(painter, cx, head_cy, r, fur_color):
    painter.setPen(NO_PEN)
    painter.setBrush(QBrush(fur_color))
    painter.drawEllipse(QPointF(cx, head_cy), r, r * 0.92)

    muzzle = QRectF(cx - r * 0.42, head_cy + r * 0.15, r * 0.84, r * 0.55)
    painter.setPen(NO_PEN)
    painter.setBrush(QBrush(BELLY))
    painter.drawEllipse(muzzle)


def _draw_stripes(painter, cx, base_y, body_w, body_h, head_cy, head_r, stripe_color):
    """Phase 6: tabby pattern-swap -- a few short strokes, palette-aware
    (derived from the current fur color, not a fixed color)."""
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.setPen(_round_pen(stripe_color, body_w * 0.05))

    for i in range(3):
        sx = cx - body_w * 0.26 + body_w * 0.26 * i
        top_y = base_y - body_h * 0.62
        path = QPainterPath()
        path.moveTo(sx, top_y)
        path.quadTo(sx + body_w * 0.06, top_y + body_h * 0.14, sx + body_w * 0.03, top_y + body_h * 0.26)
        painter.drawPath(path)

    painter.drawLine(
        QPointF(cx - head_r * 0.18, head_cy - head_r * 0.55),
        QPointF(cx - head_r * 0.05, head_cy - head_r * 0.35),
    )
    painter.drawLine(
        QPointF(cx + head_r * 0.18, head_cy - head_r * 0.55),
        QPointF(cx + head_r * 0.05, head_cy - head_r * 0.35),
    )


def _draw_face(painter, state, cx, head_cy, r, now, nose_color=PINK):
    mood = state["mood"]
    eye_wide = state["pose"]["eye_wide"]
    happy = mood == "purr"
    blinking = state["is_blinking"]

    eye_y = head_cy - r * 0.05
    eye_dx = r * 0.38
    eye_w = r * (0.22 + eye_wide * 0.10)
    eye_h = r * (0.26 + eye_wide * 0.14)

    ox, oy = state["eye_offset"]

    for side in (-1, 1):
        ex = cx + side * eye_dx
        if happy or blinking:
            _draw_closed_eye(painter, ex, eye_y, eye_w, happy)
        else:
            painter.setPen(QPen(OUTLINE, 1.5))
            painter.setBrush(QBrush(EYE_WHITE))
            painter.drawEllipse(QPointF(ex, eye_y), eye_w, eye_h)

            painter.setPen(NO_PEN)
            painter.setBrush(QBrush(EYE_PUPIL))
            pupil_r = eye_w * 0.45
            clamped_ox = max(-eye_w * 0.4, min(eye_w * 0.4, ox))
            clamped_oy = max(-eye_h * 0.4, min(eye_h * 0.4, oy))
            painter.drawEllipse(QPointF(ex + clamped_ox, eye_y + clamped_oy), pupil_r, pupil_r)

    nose = QPainterPath()
    ns = r * 0.10
    nose.moveTo(cx - ns, head_cy + r * 0.22)
    nose.lineTo(cx + ns, head_cy + r * 0.22)
    nose.lineTo(cx, head_cy + r * 0.22 + ns * 0.9)
    nose.closeSubpath()
    painter.setPen(NO_PEN)
    painter.setBrush(QBrush(nose_color))
    painter.drawPath(nose)

    painter.setPen(QPen(OUTLINE, 1.5))
    mouth_y = head_cy + r * 0.32
    if happy:
        painter.drawArc(QRectF(cx - r * 0.18, mouth_y - r * 0.08, r * 0.18, r * 0.16), 0, 180 * 16)
        painter.drawArc(QRectF(cx, mouth_y - r * 0.08, r * 0.18, r * 0.16), 0, 180 * 16)
    elif mood == "pounce":
        painter.setBrush(QBrush(OUTLINE))
        painter.drawEllipse(QPointF(cx, mouth_y + r * 0.03), r * 0.08, r * 0.08)
    else:
        painter.drawArc(QRectF(cx - r * 0.12, mouth_y - r * 0.04, r * 0.24, r * 0.12), 200 * 16, 140 * 16)


def _draw_closed_eye(painter, ex, ey, w, happy):
    path = QPainterPath()
    painter.setPen(QPen(OUTLINE, 2))
    if happy:
        path.moveTo(ex - w * 0.5, ey + w * 0.15)
        path.quadTo(ex, ey - w * 0.5, ex + w * 0.5, ey + w * 0.15)
    else:
        path.moveTo(ex - w * 0.5, ey)
        path.lineTo(ex + w * 0.5, ey)
    painter.drawPath(path)


def _draw_tail(painter, cx, base_y, body_w, now, mood, fur_color):
    if mood == "pounce":
        wag = 0.05
    elif mood == "purr":
        wag = math.sin(now * 6.0) * 0.35
    else:
        wag = math.sin(now * 1.6) * 0.5

    root_x = cx + body_w * 0.42
    root_y = base_y - body_w * 0.10

    path = QPainterPath()
    path.moveTo(root_x, root_y)
    ctrl1 = QPointF(root_x + body_w * (0.35 + wag * 0.3), root_y - body_w * 0.25)
    ctrl2 = QPointF(root_x + body_w * (0.25 + wag * 0.5), root_y - body_w * 0.65)
    tip = QPointF(root_x + body_w * (0.10 + wag * 0.6), root_y - body_w * 0.85)
    path.cubicTo(ctrl1, ctrl2, tip)

    painter.setPen(_round_pen(fur_color, body_w * 0.16))
    painter.drawPath(path)


def _draw_puppy_tail(painter, cx, base_y, body_w, now, mood, fur_color):
    """Shorter and faster-wagging than the cat's tail -- happier by
    default rather than idle-slow."""
    if mood == "pounce":
        wag = 0.15
    elif mood == "purr":
        wag = math.sin(now * 9.0) * 0.6
    else:
        wag = math.sin(now * 5.5) * 0.55

    root_x = cx + body_w * 0.40
    root_y = base_y - body_w * 0.08

    # Bulges out well past the body's right edge before curving back up and
    # in, same shape language as the cat's tail (just shorter/stubbier) --
    # a gentler curve stays hidden behind the body, drawn afterward.
    path = QPainterPath()
    path.moveTo(root_x, root_y)
    ctrl1 = QPointF(root_x + body_w * (0.42 + wag * 0.20), root_y - body_w * 0.20)
    ctrl2 = QPointF(root_x + body_w * (0.38 + wag * 0.35), root_y - body_w * 0.48)
    tip = QPointF(root_x + body_w * (0.18 + wag * 0.5), root_y - body_w * 0.60)
    path.cubicTo(ctrl1, ctrl2, tip)

    painter.setPen(_round_pen(fur_color, body_w * 0.13))
    painter.drawPath(path)


def _draw_steam_particles(painter, particles, cx, top_y):
    painter.setPen(NO_PEN)
    for p in particles:
        life_frac = p["age"] / p["life"]
        alpha = (1.0 - life_frac) * 160
        radius = 3.0 + life_frac * 4.0
        color = QColor(STEAM)
        color.setAlpha(max(0, int(alpha)))
        painter.setBrush(QBrush(color))
        painter.drawEllipse(QPointF(cx + p["dx"], top_y - p["rise"]), radius, radius)


def _draw_thinking_dots(painter, cx, top_y, now):
    """Phase 7: a little "..." while a known AI coding tool is running."""
    painter.setPen(NO_PEN)
    for i in range(3):
        phase = now * 4.0 - i * 0.6
        bob = math.sin(phase) * 3.0
        alpha = 120 + int(math.sin(phase) * 60)
        color = QColor(120, 150, 220)
        color.setAlpha(max(60, alpha))
        painter.setBrush(QBrush(color))
        painter.drawEllipse(QPointF(cx - 10 + i * 10, top_y + bob), 2.5, 2.5)
