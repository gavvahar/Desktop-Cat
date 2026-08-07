"""Phase 11: short sound cues layered onto reactions that already exist
(mouse-hunt/pounce, purr, feed, kneading). Same best-effort, fail-silently
philosophy as peek.py/audio.py -- no audio device/backend available just
means no sound, not a crash. Cues are plain sine-wave blips synthesized at
runtime with the stdlib `wave`/`struct` modules (no external asset files,
no new pip dependency), the same way the app stayed asset-free procedural
for visuals. Plain functions -- no classes (QSoundEffect instances are
held in a module-level dict, same as using QLabel/QTimer instances
elsewhere in this app).
"""

import math, os, struct, tempfile, wave

SAMPLE_RATE = 22050
CUE_VOLUME = 0.35  # headroom below full scale so the sine doesn't clip

# cue name -> list of (freq_hz, duration_s) tone segments, played back to back
CUES = {
    "hunt": [(660.0, 0.06), (880.0, 0.05)],
    "pounce": [(220.0, 0.05), (140.0, 0.09)],
    "purr": [(340.0, 0.10)],
    "feed": [(520.0, 0.05), (700.0, 0.05), (940.0, 0.07)],
    "knead": [(480.0, 0.04)],
}

_CACHE_DIR = os.path.join(tempfile.gettempdir(), "desktopcat-sounds")
_effects = {}  # cue name -> QSoundEffect, built lazily on first play


def _synth_wav(path, segments):
    with wave.open(path, "w") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)  # 16-bit PCM
        wav_file.setframerate(SAMPLE_RATE)
        frames = bytearray()
        for freq, duration in segments:
            n = int(SAMPLE_RATE * duration)
            for i in range(n):
                envelope = 1.0 - (i / n)  # linear fade-out avoids a click at the cut
                sample = math.sin(2 * math.pi * freq * i / SAMPLE_RATE) * CUE_VOLUME * envelope
                frames += struct.pack("<h", int(sample * 32767))
        wav_file.writeframes(bytes(frames))


def _load_effect(name):
    from PySide6.QtCore import QUrl
    from PySide6.QtMultimedia import QSoundEffect

    os.makedirs(_CACHE_DIR, exist_ok=True)
    path = os.path.join(_CACHE_DIR, f"{name}.wav")
    if not os.path.isfile(path):
        _synth_wav(path, CUES[name])

    effect = QSoundEffect()
    effect.setSource(QUrl.fromLocalFile(path))
    effect.setVolume(1.0)
    return effect


def play_cue(state, name):
    """Fire-and-forget; never raises, whether QtMultimedia is unavailable,
    there's no audio backend/device, or the temp dir isn't writable."""
    if not state["config"].get("sound", {}).get("enabled", True):
        return
    try:
        effect = _effects.get(name)
        if effect is None:
            effect = _load_effect(name)
            _effects[name] = effect
        effect.play()
    except Exception:
        pass
