"""Phase 5: stretch / water / Pomodoro / custom reminders, plus a pinned
message -- all shown in one floating bubble above the cat, in priority
order (active reminder > Pomodoro countdown > pinned message). Plain
functions operating on the state dict -- no classes.
"""

from desktopcat import state as st


def build_reminder_schedule(config, now):
    schedule = []
    reminders_cfg = config["reminders"]

    if reminders_cfg["stretch"]["enabled"]:
        interval = reminders_cfg["stretch"]["interval_minutes"] * 60
        schedule.append({"kind": "stretch", "text": _stretch_text(config), "interval": interval, "next_at": now + interval})

    if reminders_cfg["water"]["enabled"]:
        interval = reminders_cfg["water"]["interval_minutes"] * 60
        schedule.append({"kind": "water", "text": _water_text(config), "interval": interval, "next_at": now + interval})

    for custom in reminders_cfg["custom"]:
        interval = max(1, custom.get("interval_minutes", 60)) * 60
        schedule.append({"kind": "custom", "text": custom.get("text", ""), "interval": interval, "next_at": now + interval})

    return schedule


def _greeting(config):
    name = config.get("name", "").strip()
    return f"{name}, " if name else ""


def _stretch_text(config):
    return f"{_greeting(config)}time to stretch! \U0001f43e"


def _water_text(config):
    return f"{_greeting(config)}drink some water! \U0001f4a7"


def update_reminders(state, now):
    for reminder in state["reminder_schedule"]:
        if now >= reminder["next_at"]:
            show_message(state, reminder["text"], now, kind=reminder["kind"])
            reminder["next_at"] = now + reminder["interval"]


def show_message(state, text, now, kind="custom", duration=6.0):
    state["message_text"] = text
    state["message_expires_at"] = now + duration
    if kind == "stretch":
        state["stretch"] = st.STRETCH_REMINDER_AMOUNT


def update_message(state, now):
    if state["message_expires_at"] and now >= state["message_expires_at"]:
        state["message_text"] = ""
        state["message_expires_at"] = 0.0


def current_bubble_text(state):
    if state["message_text"]:
        return state["message_text"]
    if state["pomodoro_enabled"] and state["pomodoro_phase"] != "off":
        return _pomodoro_text(state)
    if state["pinned_message"]:
        return state["pinned_message"]
    return ""


def _pomodoro_text(state):
    remaining = max(0.0, state["pomodoro_phase_ends_at"] - state["last_tick"])
    minutes, seconds = divmod(int(remaining), 60)
    icon = "\U0001f345" if state["pomodoro_phase"] == "focus" else "☕"
    return f"{icon} {minutes:02d}:{seconds:02d}"


def start_pomodoro(state, config, now):
    state["pomodoro_enabled"] = True
    state["pomodoro_phase"] = "focus"
    state["pomodoro_focus_s"] = config["pomodoro"]["focus_minutes"] * 60
    state["pomodoro_break_s"] = config["pomodoro"]["break_minutes"] * 60
    state["pomodoro_phase_ends_at"] = now + state["pomodoro_focus_s"]
    state["pomodoro_cycles"] = 0


def stop_pomodoro(state):
    state["pomodoro_enabled"] = False
    state["pomodoro_phase"] = "off"


def update_pomodoro(state, now):
    if not state["pomodoro_enabled"] or state["pomodoro_phase"] == "off":
        return
    if now < state["pomodoro_phase_ends_at"]:
        return
    if state["pomodoro_phase"] == "focus":
        state["pomodoro_phase"] = "break"
        state["pomodoro_phase_ends_at"] = now + state["pomodoro_break_s"]
        show_message(state, "Break time! ☕", now, kind="pomodoro")
    else:
        state["pomodoro_cycles"] += 1
        state["pomodoro_phase"] = "focus"
        state["pomodoro_phase_ends_at"] = now + state["pomodoro_focus_s"]
        show_message(state, "Back to focus! \U0001f345", now, kind="pomodoro")
