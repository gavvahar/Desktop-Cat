"""Single source of truth for the cat's runtime state.

No classes: state lives in one module-level dict and every other module
reads/mutates it through plain functions.
"""

import random, time

WINDOW_SIZE = 140  # square window, px

# -- tuning constants (Phase 1: "tune eye-follow easing & idle blink") -----
EYE_EASE_SPEED = 12.0  # higher = snappier eye tracking (per second)
EYE_MAX_OFFSET = 5.0  # px the pupil can travel from eye center

BLINK_MIN_INTERVAL = 2.0  # seconds
BLINK_MAX_INTERVAL = 6.0
BLINK_DURATION = 0.12

HUNT_VELOCITY = 900.0  # px/s cursor speed that triggers mouse-hunt
POUNCE_DECEL = 700.0  # px/s^2 deceleration spike that triggers a pounce
POUNCE_DURATION = 0.35

PURR_MAX_VELOCITY = 70.0  # px/s: cursor must be moving slowly to "pet"
HEAD_REGION_FRACTION = 0.45  # top fraction of the window counted as "head"

CURSOR_HISTORY_LEN = 6

# -- tuning constants (Phase 2: "mochi drag" + gravity) ---------------------
LIFT_SQUASH = 0.30  # instant squash amount when picked up (0..1)
SPRING_K = 90.0  # squash/stretch spring stiffness
SPRING_DAMPING = 9.0  # squash/stretch spring damping
DRAG_STRETCH_DIVISOR = 900.0  # px/s of vertical drag speed -> full stretch target
MAX_DRAG_STRETCH = 0.45

SHAKE_VELOCITY_THRESHOLD = 250.0  # px/s horizontal speed to count as a shake
SHAKE_ENERGY_GAIN = 0.45
SHAKE_ENERGY_DECAY = 3.0  # per second
MAX_SHAKE_ENERGY = 1.5
WOBBLE_FREQ = 18.0  # rad/s
MAX_WOBBLE_RAD = 0.22

GRAVITY = 2200.0  # px/s^2
MAX_FALL_SPEED = 2600.0  # px/s
LANDING_SQUASH_SCALE = 0.55  # fraction of MAX_FALL_SPEED -> full landing squash

# -- tuning constants (Phase 3: kneading anim + overheat) -------------------
KNEADING_HOLD = 0.35  # seconds a keypress keeps the kneading envelope up
KNEAD_ENVELOPE_SPEED = 10.0  # per second, envelope rise/fall rate
KNEAD_CYCLE_SPEED = 9.0  # rad/s, paw alternation speed

KEY_RATE_WINDOW = 1.5  # seconds of keypress history kept for rate calc
OVERHEAT_RATE_MIN = 4.0  # presses/s where heat starts rising
OVERHEAT_RATE_MAX = 10.0  # presses/s where heat is fully maxed
HEAT_RISE_SPEED = 2.5  # per second
HEAT_FALL_SPEED = 0.8  # per second, cools slower than it heats up

STEAM_SPAWN_HEAT_MIN = 0.35  # heat must exceed this before steam appears
STEAM_SPAWN_RATE = 6.0  # particles/s at heat == 1.0
STEAM_LIFE_MIN = 0.7
STEAM_LIFE_MAX = 1.3
STEAM_DRIFT_MIN = 18.0  # px/s upward
STEAM_DRIFT_MAX = 34.0

# -- tuning constants (Phase 4: paper unroll on scroll) ---------------------
SCROLL_HOLD = 0.35  # seconds a scroll event keeps the unroll envelope up
SCROLL_ENVELOPE_SPEED = 8.0  # per second, unroll/re-roll rate

# -- tuning constants (Phase 5: timers & reminders) --------------------------
STRETCH_REMINDER_AMOUNT = 0.4  # instant grow/stretch impulse on a stretch reminder

# -- tuning constants (Phase 7: peek mode + AI-agent hooks) ------------------
PEEK_EASE_SPEED = 4.0  # per second, slide-to-edge/back rate


def new_state():
    now = time.monotonic()
    return {
        "window_pos": (100, 100),
        "dragging": False,
        "drag_grab_offset": (0, 0),
        "cursor_history": [],  # list of (t, x, y), most recent last
        "cursor_velocity": 0.0,  # px/s, scalar magnitude
        "cursor_dir": (0.0, 0.0),  # unit vector, last known direction
        "eye_offset": [0.0, 0.0],  # current eased pupil offset
        "eye_target": [0.0, 0.0],  # desired pupil offset this frame
        "is_blinking": False,
        "blink_ends_at": 0.0,
        "next_blink_at": now + random.uniform(BLINK_MIN_INTERVAL, BLINK_MAX_INTERVAL),
        "mood": "idle",  # idle | hunt | pounce | purr
        "pounce_ends_at": 0.0,
        "kneading": False,
        "kneading_ends_at": 0.0,
        "knead_envelope": 0.0,
        "knead_phase": 0.0,
        "key_press_times": [],
        "heat": 0.0,
        "steam_particles": [],  # list of {dx, rise, age, life, drift_speed}
        "scrolling": False,
        "scroll_ends_at": 0.0,
        "scroll_unroll": 0.0,
        "config": {},
        "reminder_schedule": [],  # list of {kind, text, interval, next_at}
        "message_text": "",
        "message_expires_at": 0.0,
        "pinned_message": "",
        "pomodoro_enabled": False,
        "pomodoro_phase": "off",  # off | focus | break
        "pomodoro_phase_ends_at": 0.0,
        "pomodoro_focus_s": 0.0,
        "pomodoro_break_s": 0.0,
        "pomodoro_cycles": 0,
        "prev_window_pos": (100, 100),
        "drag_vx": 0.0,
        "drag_vy": 0.0,
        "shake_energy": 0.0,
        "wobble_angle": 0.0,
        "stretch": 0.0,
        "stretch_vel": 0.0,
        "falling": False,
        "fall_vy": 0.0,
        "floor_y": 100,
        "screen_right": 100,
        "peek_mode": False,
        "peek_check_next_at": 0.0,
        "peek_rest_x": 100,
        "peek_target_x": 100,
        "ai_active": False,
        "ai_watch_next_at": 0.0,
        "ai_poll_running": False,
        "ai_poll_result": None,  # set by the background poll thread; None until the first one finishes
        "hunger": 0.0,  # 0.0 = just fed, rises toward 1.0 = starving
        "hunger_nagged": False,  # one-shot: already showed the nag bubble this hungry-streak
        "eat_ends_at": 0.0,
        "audio_playing": False,
        "audio_next_at": 0.0,
        "audio_poll_running": False,
        "audio_poll_result": None,  # set by the background poll thread; None until the first one finishes
        "pose": {
            "crouch": 0.0,
            "ear_flatten": 0.0,
            "eye_wide": 0.0,
            "paws_forward": 0.0,
        },
        "last_tick": now,
    }


POSE_EASE_SPEED = 10.0  # per second

POSE_TARGETS = {
    "idle": {"crouch": 0.0, "ear_flatten": 0.0, "eye_wide": 0.0, "paws_forward": 0.0},
    "hunt": {"crouch": 0.5, "ear_flatten": 0.7, "eye_wide": 1.0, "paws_forward": 0.1},
    "pounce": {"crouch": 0.8, "ear_flatten": 0.9, "eye_wide": 1.0, "paws_forward": 1.0},
    "purr": {"crouch": 0.1, "ear_flatten": 0.0, "eye_wide": 0.0, "paws_forward": 0.0},
    "eat": {"crouch": 0.3, "ear_flatten": 0.1, "eye_wide": 0.0, "paws_forward": 0.8},
}
