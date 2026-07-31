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
}
