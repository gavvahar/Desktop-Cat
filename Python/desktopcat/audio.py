"""Best-effort, cross-platform detection of "is the system currently
playing audio" -- used to draw headphones on the pet. Same philosophy as
peek.py/ai_hooks.py: every platform probe is wrapped in try/except and
silently reports False (headphones just never appear) if it can't run in
the current environment. Polled off the GUI thread like ai_hooks.py, since
a subprocess/COM call could take noticeably longer than one frame. Plain
functions -- no classes.
"""

import platform, subprocess, threading

AUDIO_POLL_INTERVAL = 1.5  # seconds between playing/not-playing checks
AUDIO_POLL_TIMEOUT = 3.0  # generous, since it no longer blocks the GUI thread
AUDIO_PEAK_THRESHOLD = 0.01  # Windows meter peak (0.0-1.0) above which we call it "playing"

_poll_lock = threading.Lock()


def _is_audio_playing_linux():
    # pactl ships with pulseaudio-utils, and PipeWire's pipewire-pulse
    # shim provides the same CLI, so this covers the large majority of
    # modern Linux desktops without a new pip dependency. "Corked: no" is
    # the field that distinguishes an actively-playing stream from one
    # that's merely open but paused (e.g. a paused browser tab).
    try:
        out = subprocess.run(
            ["pactl", "list", "sink-inputs"],
            capture_output=True,
            text=True,
            timeout=AUDIO_POLL_TIMEOUT,
        )
        return "Corked: no" in out.stdout
    except Exception:
        return False


def _is_audio_playing_windows():
    # pycaw wraps the WASAPI IAudioMeterInformation COM interface -- no
    # built-in Windows CLI exposes per-moment "is anything playing", so
    # this is the one place a new pip dependency is actually justified.
    try:
        from pycaw.pycaw import AudioUtilities, IAudioMeterInformation
        from comtypes import CLSCTX_ALL
    except Exception:
        return False
    try:
        speakers = AudioUtilities.GetSpeakers()
        # GetSpeakers() returns pycaw's AudioDevice wrapper, not the raw
        # IMMDevice -- the COM object with .Activate() is its private _dev.
        interface = speakers._dev.Activate(IAudioMeterInformation._iid_, CLSCTX_ALL, None)
        meter = interface.QueryInterface(IAudioMeterInformation)
        return meter.GetPeakValue() > AUDIO_PEAK_THRESHOLD
    except Exception:
        return False


def _is_audio_playing_macos():
    # No dependency-free, CLI-shellable way to query "is audio playing"
    # system-wide on macOS -- would need pyobjc + CoreAudio bindings for a
    # single boolean. Documented gap, same as peek mode's "doesn't work on
    # macOS": headphones simply never appear there.
    return False


def _is_audio_playing():
    try:
        system = platform.system()
        if system == "Linux":
            return _is_audio_playing_linux()
        if system == "Windows":
            return _is_audio_playing_windows()
        if system == "Darwin":
            return _is_audio_playing_macos()
        return False
    except Exception:
        return False


def _poll_in_background(state):
    playing = _is_audio_playing()
    with _poll_lock:
        state["audio_poll_result"] = playing
    state["audio_poll_running"] = False


def update_audio_watch(state, now):
    if now >= state["audio_next_at"] and not state["audio_poll_running"]:
        state["audio_next_at"] = now + AUDIO_POLL_INTERVAL
        state["audio_poll_running"] = True
        threading.Thread(target=_poll_in_background, args=(state,), daemon=True).start()

    with _poll_lock:
        result = state["audio_poll_result"]

    if result is None:
        return
    state["audio_playing"] = result
