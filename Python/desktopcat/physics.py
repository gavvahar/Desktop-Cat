"""Mochi drag physics (Phase 2): squash/stretch on lift, wobble on shake,
settle on drop, and simple gravity to rest on the screen bottom. Plain
functions operating on the state dict from state.py -- no classes.
"""

import math

from desktopcat import state as st


def on_pick_up(state):
    state["stretch"] = -st.LIFT_SQUASH
    state["stretch_vel"] = 0.0
    state["shake_energy"] = 0.0


def update_drag_physics(state, dt, now):
    px, py = state["prev_window_pos"]
    wx, wy = state["window_pos"]
    raw_vx, raw_vy = (wx - px) / dt, (wy - py) / dt

    # Shake detection needs the raw per-tick velocity -- smoothing (below)
    # would wash out the fast reversals a "shake" actually consists of.
    prev_raw_vx = state.get("_prev_raw_vx", 0.0)
    reversed_direction = prev_raw_vx * raw_vx < 0
    is_fast = abs(raw_vx) > st.SHAKE_VELOCITY_THRESHOLD
    if reversed_direction and is_fast:
        state["shake_energy"] = min(st.MAX_SHAKE_ENERGY, state["shake_energy"] + st.SHAKE_ENERGY_GAIN)
    state["_prev_raw_vx"] = raw_vx

    # Smoothed velocity feeds the continuous stretch target, where jitter
    # would look bad.
    lerp = min(1.0, dt * 12.0)
    state["drag_vx"] += (raw_vx - state["drag_vx"]) * lerp
    state["drag_vy"] += (raw_vy - state["drag_vy"]) * lerp

    state["shake_energy"] *= max(0.0, 1.0 - st.SHAKE_ENERGY_DECAY * dt)
    state["wobble_angle"] = math.sin(now * st.WOBBLE_FREQ) * state["shake_energy"] * st.MAX_WOBBLE_RAD


def update_squash_spring(state, dt):
    target = 0.0
    if state["dragging"]:
        target = max(-st.MAX_DRAG_STRETCH, min(st.MAX_DRAG_STRETCH, state["drag_vy"] / st.DRAG_STRETCH_DIVISOR))
    else:
        state["wobble_angle"] *= max(0.0, 1.0 - st.SHAKE_ENERGY_DECAY * dt)
        state["shake_energy"] = 0.0

    accel = -st.SPRING_K * (state["stretch"] - target) - st.SPRING_DAMPING * state["stretch_vel"]
    state["stretch_vel"] += accel * dt
    state["stretch"] += state["stretch_vel"] * dt


def start_falling(state):
    _, wy = state["window_pos"]
    if wy < state["floor_y"] - 1:
        state["falling"] = True
        state["fall_vy"] = 0.0


def update_gravity(state, dt):
    if not state["falling"]:
        return

    state["fall_vy"] = min(st.MAX_FALL_SPEED, state["fall_vy"] + st.GRAVITY * dt)
    wx, wy = state["window_pos"]
    new_y = wy + state["fall_vy"] * dt

    if new_y >= state["floor_y"]:
        new_y = state["floor_y"]
        impact_ratio = min(1.0, state["fall_vy"] / st.MAX_FALL_SPEED)
        state["stretch"] = -st.LANDING_SQUASH_SCALE * impact_ratio
        state["stretch_vel"] = 0.0
        state["falling"] = False
        state["fall_vy"] = 0.0

    state["window_pos"] = (wx, new_y)
