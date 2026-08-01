"""Phase 7: best-effort "AI-agent" hooks -- thinking-along + done-jump for
Claude Code / Codex / Cursor. Per the plan: "no standard API for this;
watch process state / logs per tool. Most bespoke -- do it last." This is
the crudest possible version of that: poll the process list for known
names. Plain functions -- no classes.
"""

import platform, subprocess

AI_PROCESS_NAMES = ("claude", "codex", "cursor")
POLL_INTERVAL = 2.0  # seconds between process-list polls
DONE_JUMP_AMOUNT = 0.5  # squash/stretch impulse (see physics.py's spring)


def _running_process_names():
    try:
        if platform.system() == "Windows":
            out = subprocess.run(["tasklist"], capture_output=True, text=True, timeout=2)
        else:
            out = subprocess.run(["ps", "-eo", "comm"], capture_output=True, text=True, timeout=2)
        return out.stdout.lower()
    except Exception:
        return ""


def update_ai_watch(state, now):
    if now < state["ai_watch_next_at"]:
        return
    state["ai_watch_next_at"] = now + POLL_INTERVAL

    names = _running_process_names()
    active = any(proc in names for proc in AI_PROCESS_NAMES)

    if state["ai_active"] and not active:
        state["stretch"] = DONE_JUMP_AMOUNT  # "done jump" -- reuses the mochi spring
    state["ai_active"] = active
