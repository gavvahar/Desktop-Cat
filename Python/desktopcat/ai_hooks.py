"""Phase 7: best-effort "AI-agent" hooks -- thinking-along + done-jump for
Claude Code / Codex / Cursor. Per the plan: "no standard API for this;
watch process state / logs per tool. Most bespoke -- do it last." This is
the crudest possible version of that: poll the process list for known
names. Plain functions -- no classes (the background Thread is a stdlib
class instance, same as QTimer/QLabel/QMenu elsewhere -- not a class
defined here).

The poll runs off the GUI thread deliberately: measured on real Windows,
`tasklist` alone takes ~2 seconds. Calling that synchronously from tick()
(the Qt timer callback) would freeze the whole app for ~2 of every 2
seconds -- which is exactly the "app freezes" bug this replaced. A
background thread means tick() never waits on it; it just picks up
whatever the most recently finished poll found.
"""

import platform, subprocess, threading

AI_PROCESS_NAMES = ("claude", "codex", "cursor")
POLL_INTERVAL = 2.0  # seconds between process-list polls
POLL_TIMEOUT = 5.0  # generous since it no longer blocks the GUI thread
DONE_JUMP_AMOUNT = 0.5  # squash/stretch impulse (see physics.py's spring)

_poll_lock = threading.Lock()


def _running_process_names():
    try:
        if platform.system() == "Windows":
            # CREATE_NO_WINDOW: this app is built --windowed (no console of
            # its own), so without this flag Windows flashes a new console
            # window into existence for every single poll.
            kwargs = {"creationflags": subprocess.CREATE_NO_WINDOW} if hasattr(subprocess, "CREATE_NO_WINDOW") else {}
            out = subprocess.run(["tasklist"], capture_output=True, text=True, timeout=POLL_TIMEOUT, **kwargs)
        else:
            out = subprocess.run(["ps", "-eo", "comm"], capture_output=True, text=True, timeout=POLL_TIMEOUT)
        return out.stdout.lower()
    except Exception:
        return ""


def _poll_in_background(state):
    names = _running_process_names()
    active = any(proc in names for proc in AI_PROCESS_NAMES)
    with _poll_lock:
        state["ai_poll_result"] = active
    state["ai_poll_running"] = False


def update_ai_watch(state, now):
    if now >= state["ai_watch_next_at"] and not state["ai_poll_running"]:
        state["ai_watch_next_at"] = now + POLL_INTERVAL
        state["ai_poll_running"] = True
        threading.Thread(target=_poll_in_background, args=(state,), daemon=True).start()

    with _poll_lock:
        result = state["ai_poll_result"]

    if result is None:
        return
    if state["ai_active"] and not result:
        state["stretch"] = DONE_JUMP_AMOUNT  # "done jump" -- reuses the mochi spring
    state["ai_active"] = result
