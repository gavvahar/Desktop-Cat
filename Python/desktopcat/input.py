"""Cursor / keyboard reaction logic. Plain functions only, operating on the
state dict from state.py.
"""

import random, time

from desktopcat import sound
from desktopcat import state as st


def push_cursor_sample(state, x, y, now):
    history = state["cursor_history"]
    history.append((now, x, y))
    if len(history) > st.CURSOR_HISTORY_LEN:
        del history[0]


def _velocity_between(a, b):
    t0, x0, y0 = a
    t1, x1, y1 = b
    dt = t1 - t0
    if dt <= 0:
        return 0.0, 0.0, 0.0
    dx, dy = x1 - x0, y1 - y0
    return (dx / dt, dy / dt, dt)


def update_cursor_velocity(state):
    history = state["cursor_history"]
    if len(history) < 2:
        state["cursor_velocity"] = 0.0
        return

    vx, vy, _dt = _velocity_between(history[-2], history[-1])
    speed = (vx**2 + vy**2) ** 0.5

    prev_speed = state["cursor_velocity"]
    state["cursor_velocity"] = speed
    state["_cursor_accel"] = speed - prev_speed  # can be negative (deceleration)

    if speed > 1.0:
        state["cursor_dir"] = (vx / speed, vy / speed)


def point_in_head_region(window_pos, cursor_pos):
    wx, wy = window_pos
    cx, cy = cursor_pos
    local_x = cx - wx
    local_y = cy - wy
    if not (0 <= local_x <= st.WINDOW_SIZE):
        return False
    return 0 <= local_y <= st.WINDOW_SIZE * st.HEAD_REGION_FRACTION


def update_mood(state, now, cursor_pos):
    if now < state["pounce_ends_at"]:
        state["mood"] = "pounce"
        return

    if now < state["eat_ends_at"]:
        state["mood"] = "eat"
        return

    velocity = state["cursor_velocity"]
    decel = state.get("_cursor_accel", 0.0)

    was_hunting = state["mood"] in ("hunt", "pounce")
    if was_hunting and decel < -st.POUNCE_DECEL:
        state["mood"] = "pounce"
        state["pounce_ends_at"] = now + st.POUNCE_DURATION
        sound.play_cue(state, "pounce")
        return

    if velocity > st.HUNT_VELOCITY:
        if state["mood"] != "hunt":
            sound.play_cue(state, "hunt")
        state["mood"] = "hunt"
        return

    over_head = point_in_head_region(state["window_pos"], cursor_pos)
    if over_head and 0 < velocity < st.PURR_MAX_VELOCITY:
        if state["mood"] != "purr":
            sound.play_cue(state, "purr")
        state["mood"] = "purr"
        return

    if _should_sleep(state, now):
        state["mood"] = "sleep"
        return

    state["mood"] = "idle"


def _in_night_window(start_hour, end_hour):
    if start_hour == end_hour:
        return False
    hour = time.localtime().tm_hour
    if start_hour < end_hour:
        return start_hour <= hour < end_hour
    return hour >= start_hour or hour < end_hour  # wraps past midnight


def _should_sleep(state, now):
    sleep_cfg = state["config"]["sleep"]
    if now - state["last_activity_at"] >= sleep_cfg["idle_minutes"] * 60:
        return True
    if sleep_cfg["night_mode_enabled"]:
        return _in_night_window(sleep_cfg["night_start_hour"], sleep_cfg["night_end_hour"])
    return False


def update_activity(state, now):
    """Refreshes last_activity_at on any real interaction -- used by
    _should_sleep to know how long the pet has been left alone. Checked
    independently of mood since dragging/kneading/scrolling don't set mood."""
    active = state["dragging"] or state["kneading"] or state["scrolling"] or state["mood"] in ("hunt", "purr", "pounce", "eat")
    if active:
        state["last_activity_at"] = now


def update_eye_target(state, cursor_pos):
    wx, wy = state["window_pos"]
    center_x = wx + st.WINDOW_SIZE / 2
    center_y = wy + st.WINDOW_SIZE * 0.4  # eyes sit above vertical center
    dx = cursor_pos[0] - center_x
    dy = cursor_pos[1] - center_y
    dist = (dx**2 + dy**2) ** 0.5
    if dist < 1e-3:
        state["eye_target"] = [0.0, 0.0]
        return
    scale = min(1.0, dist / 400.0) * st.EYE_MAX_OFFSET
    state["eye_target"] = [dx / dist * scale, dy / dist * scale]


def ease_eyes(state, dt):
    tx, ty = state["eye_target"]
    ex, ey = state["eye_offset"]
    lerp = 1.0 - pow(2.71828, -st.EYE_EASE_SPEED * dt)  # frame-rate independent ease
    state["eye_offset"] = [ex + (tx - ex) * lerp, ey + (ty - ey) * lerp]


def update_blink(state, now):
    if state["is_blinking"]:
        if now >= state["blink_ends_at"]:
            state["is_blinking"] = False
            state["next_blink_at"] = now + random.uniform(st.BLINK_MIN_INTERVAL, st.BLINK_MAX_INTERVAL)
        return

    if now >= state["next_blink_at"]:
        state["is_blinking"] = True
        state["blink_ends_at"] = now + st.BLINK_DURATION


def start_drag(state, global_pos, window_pos):
    state["dragging"] = True
    state["drag_grab_offset"] = (
        global_pos[0] - window_pos[0],
        global_pos[1] - window_pos[1],
    )


def drag_to(state, global_pos):
    gx, gy = state["drag_grab_offset"]
    return (global_pos[0] - gx, global_pos[1] - gy)


def end_drag(state):
    state["dragging"] = False


def on_key_press(state, now):
    # Runs on the pynput listener thread -- only ever touches plain dict
    # fields here, never a Qt object (QSoundEffect.play() included), same
    # rule the rest of this app follows for its background threads.
    state["kneading"] = True
    state["kneading_ends_at"] = now + st.KNEADING_HOLD
    state["key_press_times"].append(now)


def update_kneading(state, now):
    if state["kneading"] and now >= state["kneading_ends_at"]:
        state["kneading"] = False


def update_kneading_anim(state, dt):
    # Runs on the GUI thread (called from tick()), unlike on_key_press --
    # the right place for the one-shot "kneading just started" sound cue.
    if state["kneading"]:
        if not state["knead_cue_played"]:
            sound.play_cue(state, "knead")
            state["knead_cue_played"] = True
    else:
        state["knead_cue_played"] = False

    target = 1.0 if state["kneading"] else 0.0
    lerp = min(1.0, dt * st.KNEAD_ENVELOPE_SPEED)
    state["knead_envelope"] += (target - state["knead_envelope"]) * lerp
    state["knead_phase"] += dt * st.KNEAD_CYCLE_SPEED


def update_heat(state, now, dt):
    times = state["key_press_times"]
    cutoff = now - st.KEY_RATE_WINDOW
    while times and times[0] < cutoff:
        times.pop(0)

    rate = len(times) / st.KEY_RATE_WINDOW
    span = st.OVERHEAT_RATE_MAX - st.OVERHEAT_RATE_MIN
    target = max(0.0, min(1.0, (rate - st.OVERHEAT_RATE_MIN) / span))

    speed = st.HEAT_RISE_SPEED if target > state["heat"] else st.HEAT_FALL_SPEED
    lerp = min(1.0, dt * speed)
    state["heat"] += (target - state["heat"]) * lerp


def update_steam_particles(state, dt):
    particles = state["steam_particles"]
    for p in particles:
        p["age"] += dt
        p["rise"] += p["drift_speed"] * dt
    state["steam_particles"] = [p for p in particles if p["age"] < p["life"]]

    if state["heat"] < st.STEAM_SPAWN_HEAT_MIN:
        return
    spawn_chance = (state["heat"] - st.STEAM_SPAWN_HEAT_MIN) * st.STEAM_SPAWN_RATE * dt
    if random.random() < spawn_chance:
        state["steam_particles"].append(
            {
                "dx": random.uniform(-8.0, 8.0),
                "rise": 0.0,
                "age": 0.0,
                "life": random.uniform(st.STEAM_LIFE_MIN, st.STEAM_LIFE_MAX),
                "drift_speed": random.uniform(st.STEAM_DRIFT_MIN, st.STEAM_DRIFT_MAX),
            }
        )


def on_scroll(state, now):
    state["scrolling"] = True
    state["scroll_ends_at"] = now + st.SCROLL_HOLD


def update_scrolling(state, now):
    if state["scrolling"] and now >= state["scroll_ends_at"]:
        state["scrolling"] = False


def update_scroll_anim(state, dt):
    target = 1.0 if state["scrolling"] else 0.0
    lerp = min(1.0, dt * st.SCROLL_ENVELOPE_SPEED)
    state["scroll_unroll"] += (target - state["scroll_unroll"]) * lerp


def start_scroll_listener(state):
    """Global scroll capture for the paper-unroll reaction. X11-only for
    now, same caveat as the keyboard listener.
    """
    try:
        from pynput import mouse
    except Exception as exc:
        print(f"[desktopcat] scroll reactions disabled: {exc}")
        return None

    def _on_scroll(_x, _y, _dx, _dy):
        on_scroll(state, time.monotonic())

    listener = mouse.Listener(on_scroll=_on_scroll)
    try:
        listener.start()
    except Exception as exc:
        print(f"[desktopcat] scroll reactions disabled: {exc}")
        return None
    return listener


def start_keyboard_listener(state):
    """Global keyboard capture for the kneading reaction (Phase 0 stub,
    upgraded in Phase 3). X11-only for now -- see plan's "hard parts" note
    on Wayland restricting global input.
    """
    try:
        from pynput import keyboard
    except Exception as exc:
        print(f"[desktopcat] keyboard reactions disabled: {exc}")
        return None

    def _on_press(_key):
        on_key_press(state, time.monotonic())

    listener = keyboard.Listener(on_press=_on_press)
    try:
        listener.start()
    except Exception as exc:
        print(f"[desktopcat] keyboard reactions disabled: {exc}")
        return None
    return listener


def update_pose(state, dt):
    target = st.POSE_TARGETS[state["mood"]]
    pose = state["pose"]
    lerp = 1.0 - pow(2.71828, -st.POSE_EASE_SPEED * dt)
    for key, target_value in target.items():
        pose[key] += (target_value - pose[key]) * lerp
