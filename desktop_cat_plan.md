# Desktop Pet — Build Plan

A free, open-source pixel-cat desktop companion (Comnyang-style) built in
**PySide6**, **Linux-first**. No payments, no backend, no accounts.

---

## Goal & scope

- A tiny pixel cat that lives as an always-on-top overlay, reacts to mouse /
  keyboard / scroll, and runs stretch / water / Pomodoro reminders.
- **Free forever.** No purchase flow, no license server, no telemetry.
- Ship as source on GitHub + an AppImage and Flatpak.

## Stack

| Layer         | Choice                                          | Why                                                      |
| ------------- | ----------------------------------------------- | -------------------------------------------------------- |
| App framework | PySide6 (Qt)                                    | Python-first, light RAM, good transparent-window support |
| Rendering     | QPainter (procedural now) → sprite sheets later | Start asset-free, swap in art                            |
| Global input  | `pynput` (X11) / `python-evdev` (Wayland)       | Reacts to input anywhere on screen                       |
| Packaging     | AppImage, Flatpak                               | Standard Linux distribution                              |
| Art tool      | Aseprite (or commission)                        | Pixel sprite sheets + palette maps                       |

## The hard parts (read before building)

1. **Frameless transparent always-on-top window** with a **shape mask** so
   clicks on empty pixels fall through to windows behind. Needs a running
   compositor (any modern DE has one).
2. **Global input capture** — the real OS challenge:
   - **X11**: easy. `QCursor.pos()` for cursor, `pynput` for keys/scroll.
   - **Wayland**: global keyboard/cursor are restricted. Fall back to reading
     `/dev/input/event*` via `python-evdev`, requires user in the `input` group.
   - **Plan: build & test on X11 first, harden for Wayland later.**
3. **AI-agent status hooks** (thinking-along, done-jump) — no standard API;
   watch process state / logs per tool. Most bespoke — do it last.

---

## Build phases

### Phase 0 — Foundation ✅ (done in v0)

- [x] Transparent, frameless, always-on-top window
- [x] Shape mask (click-through on empty space)
- [x] Procedural pixel cat (no assets needed)
- [x] Eye-follow (global cursor)
- [x] Drag the cat
- [x] Global keyboard "kneading" stub

### Phase 1 — Cursor reactions

- [x] **Mouse-hunt** — cursor velocity above a threshold → chase / pounce pose
- [x] **Pet-to-purr** — slow cursor movement over the head region → purr anim
- [x] Tune eye-follow easing & idle blink

### Phase 2 — Physics & touch

- [x] **Mochi drag** — squash/stretch on lift, wobble on shake, settle on drop
- [x] Edge/gravity behavior (optional: rest on screen bottom)

### Phase 3 — Keyboard reactions

- [x] **Kneading** anim on keypress (upgrade the stub)
- [x] **Overheat** — high keystroke rate → red tint + steam particles

### Phase 4 — Scroll

- [x] **Paper unroll** — scroll events → unspool/re-roll paper animation

### Phase 5 — Timers & reminders (pure Python — easy wins)

- [x] Stretch reminder (interval → grow/stretch anim)
- [x] Drink-water reminder
- [x] Pomodoro (focus/break loops + floating pixel timer)
- [x] Custom message reminder (interval + text, configurable in config.json; message shown in the floating bubble)
- [x] Pinned/fixed message above the cat

### Phase 6 — Personalization

- [x] Color + pattern **palette-swap** on a base sprite at runtime
- [x] "Tell your name" → use it in reminders/breaks
- [x] Settings window + persist to a local config file (JSON/TOML)

### Phase 7 — Advanced

- [x] **Peek mode** — detect fullscreen video → move to screen edge, mute reactions (X11-only, best-effort)
- [x] **AI-agent hooks** — thinking-along + done-jump for Claude Code / Codex / Cursor (best-effort process-name polling, as bespoke/crude as the plan warned)

### Phase 8 — Ship

- [x] Settings persistence (`config.json`, Phase 6) + autostart entry (`Python/desktopcat/autostart.py`: XDG autostart on Linux, Run registry key on Windows, toggled from Settings)
- [x] Package as AppImage (`packaging/appimage/build.sh`) and Flatpak (`packaging/flatpak/`; also builds a Windows `.exe` and a macOS `.app`, beyond the original plan's Linux-only scope)
- [x] GitHub repo + README + LICENSE (went with MIT -- permissive default; swap to GPL if you'd rather keep forks open)
- [ ] Draw/commission original sprite art (do NOT copy Comnyang's assets) -- left for you: this is a creative/licensing call, not something to auto-generate. The app stays asset-free procedural (QPainter) until then.

### Phase 9 — Feed the pet + audio-playing headphones

Two additive features beyond the original scope. Both reuse existing
architecture end-to-end (decaying-stat pattern like `heat`, bubble-message
pattern from `reminders.show_message`, temporary-mood pattern like
`pounce_ends_at`, and the threaded best-effort OS-probe pattern from
`ai_hooks.py`) -- no new architectural patterns needed.

- [x] **Feed the pet** -- a right-click "Feed" menu action that resets a
      hunger meter (`state["hunger"]`, rises over ~20 minutes) and triggers a
      brief "eat" mood/animation (chewing mouth in `_draw_face`, paws-forward
      pose reusing the existing `paws_forward` pose key). A one-shot nag bubble
      ("I'm hungry!") fires via `reminders.show_message` once hunger crosses a
      threshold. New `Python/desktopcat/feeding.py` module
      (`update_hunger`, `update_hunger_nag`, `feed_pet`).
- [x] **Audio-playing headphones** -- best-effort, cross-platform detection
      of whether the system is currently playing audio; draws headphones on
      the pet's head while it is (`_draw_headphones` overlay in `render.py`,
      gated by `state["audio_playing"]`, drawn last in `draw_pet` after the
      existing `_draw_thinking_dots`). New `Python/desktopcat/audio.py` module,
      structurally cloned from `ai_hooks.py` (background-threaded poll, never
      blocks the GUI thread): Linux via `pactl list sink-inputs` (no new pip
      dependency, checks for `"Corked: no"`), Windows via `pycaw`'s WASAPI
      peak-meter query (`pycaw; sys_platform == "win32"` added to
      `requirements.txt`), macOS left as a documented no-op (same accepted gap
      as peek mode) since there's no dependency-free way to query it.
- [x] Wiring: `state.py` (new fields + `POSE_TARGETS["eat"]`), `input.py`
      (`update_mood` gets an `eat_ends_at` check like `pounce_ends_at`),
      `window.py` (`show_context_menu` gets a "Feed" action; `tick()` calls
      `feeding.update_hunger`/`update_hunger_nag` and `audio.update_audio_watch`).
- [x] Verify headlessly through the real pipeline (`QT_QPA_PLATFORM=offscreen`,
      real `CatWindow` -> `tick()`/state mutation -> `repaint()` -> `grab()` ->
      pixel checks), same technique used for every prior feature -- fast-forward
      hunger by setting `state["hunger"]` directly rather than waiting real
      minutes; pixel-diff headphone-cup coordinates with `audio_playing` on/off
      for both `character = "cat"` and `"puppy"`.

### Phase 10 — Day/night-aware sleep

Reuses the existing mood/pose system rather than introducing new machinery.

- [x] A new `"sleep"` mood after a period of no interaction, or during a
      configurable night-hours window. Reuses `_draw_closed_eye` (already
      used for blinking/happy eyes) for the sleeping look, a new
      `POSE_TARGETS["sleep"]` entry, and a new `elif mood == "sleep":`
      branch in `_draw_face`. Idle tracking follows the existing
      `next_blink_at`-style timestamp pattern (a `last_activity_at` field
      updated by every real reaction trigger -- mouse-hunt/purr/feed/
      kneading/scroll); night-hours check is a plain local-time-of-day
      comparison, configurable start/end hour in Settings like the existing
      reminder toggles. Any real interaction immediately wakes the pet,
      same as how `pounce_ends_at`/`eat_ends_at` get pre-empted by fresh
      triggers.
- [x] Wiring: `state.py` (new fields + `POSE_TARGETS["sleep"]`),
      `config.py` (night-hours window), `settings_ui.py` (new controls),
      `window.py`/`input.py` (idle tracking + mood check), `render.py`
      (sleep pose/face branch).
- [x] Verify headlessly the same way as every prior feature
      (`QT_QPA_PLATFORM=offscreen`, real `CatWindow` pipeline, pixel checks
      for the sleep pose).

### Phase 11 — Sound effects (planned, not started)

Follows the same "best-effort, fail silently" philosophy as
`peek.py`/`audio.py` -- no audio device/backend available just means no
sound, not a crash.

- [ ] Short cues layered onto reactions that already exist (mouse-hunt/
      pounce, purr, feed, kneading). New `Python/desktopcat/sound.py` using
      PySide6's `QSoundEffect` (`QtMultimedia`), with a `play_cue(name)`-
      style API gated by a mute toggle in Settings/config (same
      `config.py` DEFAULTS pattern as existing toggles). Same licensing
      question sprite art already raised: real meow/bark samples would
      need sourcing/recording, not something to auto-generate -- default
      to simple procedurally-synthesized short tones/blips (plain Python
      `wave`/`struct` sine-wave generation, no external asset files) so
      the feature works out of the box, the same way the app stayed
      asset-free procedural for visuals.
- [ ] Wiring: `config.py` (mute toggle), `settings_ui.py` (new control),
      sound-cue calls added at each existing reaction's trigger site
      (mouse-hunt, purr, `feed_pet`, kneading).
- [ ] Verify by confirming `play_cue` doesn't raise when no audio backend
      is present, matching how `audio._is_audio_playing_linux()` was
      verified to fail gracefully.

---

## Art plan

- Each behavior = a sprite sheet (frame sequence). Aseprite is standard.
- "Custom color/pattern" = base sprite + palette-swap layer at runtime.
- Keep the base silhouette consistent across animations so masks line up.

## Config & data (all local)

- Single config file (e.g. `~/.config/desktopcat/config.toml`): name, colors,
  timer settings, enabled reactions.
- No network calls anywhere → "no telemetry" is automatic.

## Licensing note

- Your code is yours to write and release — pick a license (MIT or GPL).
- Cloning behavior/look is fine; **do not copy the original pixel art** — that
  asset is theirs. Make your own or commission it.

---

## Next action

All planned phases are implemented except **original sprite art** (Phase 8) -- a creative/licensing decision for a human to make, not something to
auto-generate. Everything else is code-complete; what's left is testing on
real hardware/displays (most of this was built and verified headlessly),
tuning based on how it actually feels to use, and eventually replacing the
procedural QPainter cat with real sprite sheets once art exists.
