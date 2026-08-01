# Desktop Pet — Build Plan

A free, open-source pixel-cat desktop companion (Comnyang-style) built in
**PySide6**, **Linux-first**. No payments, no backend, no accounts.

---

## Goal & scope

- A tiny pixel cat that lives as an always-on-top overlay, reacts to mouse /
  keyboard / scroll, and runs stretch / water / Pomodoro reminders.
- **Free forever.** No purchase flow, no license server, no telemetry.
- Ship as source on GitHub + an AppImage.

## Stack

| Layer         | Choice                                          | Why                                                      |
| ------------- | ----------------------------------------------- | -------------------------------------------------------- |
| App framework | PySide6 (Qt)                                    | Python-first, light RAM, good transparent-window support |
| Rendering     | QPainter (procedural now) → sprite sheets later | Start asset-free, swap in art                            |
| Global input  | `pynput` (X11) / `python-evdev` (Wayland)       | Reacts to input anywhere on screen                       |
| Packaging     | AppImage                                        | Standard Linux distribution                              |
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

- [ ] Settings persistence + autostart entry
- [x] Package as AppImage (`packaging/appimage/build.sh`)
- [ ] GitHub repo + README + LICENSE (MIT = permissive, GPL = keeps forks open)
- [ ] Draw/commission original sprite art (do NOT copy Comnyang's assets)

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

Phase 8: **ship** -- settings persistence + autostart entry, GitHub repo +
README + LICENSE, and original sprite art.
