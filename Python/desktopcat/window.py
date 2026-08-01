"""The one Qt-mandated class in this app.

PySide6 requires subclassing QWidget to override paintEvent / mouse events --
there's no classless way to do that. This class holds no behavior of its
own: every override is a one-line delegation to a plain function in
input.py / render.py, and all state lives in the module-level dict from
state.py.
"""

import time

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import QWidget

from desktopcat import input as cat_input
from desktopcat import physics
from desktopcat import render
from desktopcat import state as st

TICK_MS = 16  # ~60 fps


def is_wsl():
    """WSLg's window forwarding drops Qt.WindowType.Tool windows entirely
    (not just hides them from Alt+Tab/taskbar like on native X11/Windows --
    they never render at all). Detected via /proc/version rather than an
    env var so it doesn't depend on how the process was launched.
    """
    try:
        with open("/proc/version") as fh:
            return "microsoft" in fh.read().lower()
    except OSError:
        return False


def tick(window):
    now = time.monotonic()
    state = window.state
    dt = max(1e-4, now - state["last_tick"])
    state["last_tick"] = now

    if state["dragging"]:
        state["window_pos"] = (window.x(), window.y())
        physics.update_drag_physics(state, dt, now)
    elif state["falling"]:
        physics.update_gravity(state, dt)
        window.move(int(state["window_pos"][0]), int(state["window_pos"][1]))
    else:
        state["window_pos"] = (window.x(), window.y())

    physics.update_squash_spring(state, dt)
    state["prev_window_pos"] = state["window_pos"]

    cursor = QCursor.pos()
    cursor_pos = (cursor.x(), cursor.y())

    cat_input.push_cursor_sample(state, cursor_pos[0], cursor_pos[1], now)
    cat_input.update_cursor_velocity(state)
    if not state["dragging"]:
        cat_input.update_mood(state, now, cursor_pos)
    cat_input.update_eye_target(state, cursor_pos)
    cat_input.ease_eyes(state, dt)
    cat_input.update_blink(state, now)
    cat_input.update_kneading(state, now)
    cat_input.update_kneading_anim(state, dt)
    cat_input.update_heat(state, now, dt)
    cat_input.update_steam_particles(state, dt)
    cat_input.update_pose(state, dt)

    window.update()


class CatWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.state = st.new_state()

        flags = Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
        if not is_wsl():
            flags |= Qt.WindowType.Tool
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(st.WINDOW_SIZE, st.WINDOW_SIZE)
        self.setMask(render.build_click_mask_region(st.WINDOW_SIZE))

        screen_geo = self.screen().availableGeometry()
        start_pos = (
            screen_geo.right() - st.WINDOW_SIZE - 60,
            screen_geo.bottom() - st.WINDOW_SIZE - 60,
        )
        self.move(*start_pos)
        self.state["window_pos"] = start_pos
        self.state["prev_window_pos"] = start_pos
        self.state["floor_y"] = start_pos[1]

        self._keyboard_listener = cat_input.start_keyboard_listener(self.state)

        self._timer = QTimer(self)
        self._timer.timeout.connect(lambda: tick(self))
        self._timer.start(TICK_MS)

    def paintEvent(self, _event):
        render.paint(self, self.state, time.monotonic())

    def mousePressEvent(self, event):
        global_pos = (event.globalPosition().x(), event.globalPosition().y())
        cat_input.start_drag(self.state, global_pos, self.state["window_pos"])
        physics.on_pick_up(self.state)

    def mouseMoveEvent(self, event):
        if not self.state["dragging"]:
            return
        global_pos = (event.globalPosition().x(), event.globalPosition().y())
        new_x, new_y = cat_input.drag_to(self.state, global_pos)
        self.move(int(new_x), int(new_y))
        self.state["window_pos"] = (int(new_x), int(new_y))

    def mouseReleaseEvent(self, _event):
        cat_input.end_drag(self.state)
        physics.start_falling(self.state)
