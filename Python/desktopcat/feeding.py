"""Feed-the-pet: a hunger meter that rises over time, reset by an explicit
right-click "Feed" action, plus a one-shot nag bubble when it's been too
long without feeding. Plain functions -- no classes.
"""

from desktopcat import reminders

HUNGER_FULL_AFTER_MINUTES = 20.0  # time with no feeding to go from 0.0 -> 1.0
HUNGER_RISE_RATE = 1.0 / (HUNGER_FULL_AFTER_MINUTES * 60.0)  # per second
HUNGER_NAG_THRESHOLD = 0.7
NAG_TEXT = "I'm hungry!"
EAT_DURATION = 1.2  # seconds the "eat" mood/animation holds


def update_hunger(state, dt):
    state["hunger"] = min(1.0, state["hunger"] + HUNGER_RISE_RATE * dt)


def update_hunger_nag(state, now):
    if state["hunger"] >= HUNGER_NAG_THRESHOLD and not state["hunger_nagged"]:
        state["hunger_nagged"] = True
        reminders.show_message(state, NAG_TEXT, now, kind="hunger")


def feed_pet(state, now):
    state["hunger"] = 0.0
    state["hunger_nagged"] = False
    state["eat_ends_at"] = now + EAT_DURATION
    state["mood"] = "eat"  # set immediately so this frame's repaint already shows it
