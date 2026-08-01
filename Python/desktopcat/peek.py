"""Phase 7: peek mode -- detect a fullscreen active window and slide the
cat to the screen edge, muting reactions, until fullscreen ends.

Best-effort and X11-only (same "hard parts" caveat as global input): uses
python-xlib, already an indirect dependency via pynput on Linux. Safely
does nothing (peek mode just never triggers) if Xlib isn't importable or
any query fails -- e.g. on Windows, or if the X server doesn't cooperate.
Plain functions -- no classes.
"""

PEEK_CHECK_INTERVAL = 1.5  # seconds between fullscreen-window checks
PEEK_MARGIN = 18  # px of the cat left on-screen while peeking


def is_fullscreen_active():
    try:
        from Xlib import X, display
    except Exception:
        return False

    try:
        d = display.Display()
        root = d.screen().root

        active_atom = d.intern_atom("_NET_ACTIVE_WINDOW")
        active_prop = root.get_full_property(active_atom, X.AnyPropertyType)
        if not active_prop or not active_prop.value:
            return False
        active_id = active_prop.value[0]
        if not active_id:
            return False

        win = d.create_resource_object("window", active_id)
        state_atom = d.intern_atom("_NET_WM_STATE")
        fullscreen_atom = d.intern_atom("_NET_WM_STATE_FULLSCREEN")
        state_prop = win.get_full_property(state_atom, X.AnyPropertyType)
        if not state_prop or not state_prop.value:
            return False
        return fullscreen_atom in list(state_prop.value)
    except Exception:
        return False


def update_peek_mode(state, now):
    if now < state["peek_check_next_at"]:
        return
    state["peek_check_next_at"] = now + PEEK_CHECK_INTERVAL

    fullscreen = is_fullscreen_active()
    if fullscreen and not state["peek_mode"]:
        state["peek_mode"] = True
        state["peek_rest_x"] = state["window_pos"][0]
        state["peek_target_x"] = state["screen_right"] - PEEK_MARGIN
    elif not fullscreen and state["peek_mode"]:
        state["peek_mode"] = False
        state["peek_target_x"] = state["peek_rest_x"]
