"""Phase 6: settings dialog (right-click the cat -> Settings...). Builds
and wires up Qt's own widget classes (QDialog, QLineEdit, ...) via plain
functions -- using library-provided classes as instances isn't "defining a
class", same as QTimer/QCursor/QLabel used elsewhere in this app.
"""

import time

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QCheckBox, QColorDialog, QComboBox, QDialog, QDialogButtonBox, QFormLayout, QLineEdit, QPushButton, QSpinBox

from desktopcat import autostart
from desktopcat import config as cat_config
from desktopcat import reminders


def apply_config(window, config):
    """Hot-apply a config to the live window/state (used right after Save
    and once at startup)."""
    now = time.monotonic()
    state = window.state
    state["config"] = config
    state["reminder_schedule"] = reminders.build_reminder_schedule(config, now)
    state["pinned_message"] = config["reminders"]["pinned_message"]
    if config["pomodoro"]["enabled"]:
        reminders.start_pomodoro(state, config, now)
    else:
        reminders.stop_pomodoro(state)


def open_settings_dialog(window):
    config = window.state["config"]

    dialog = QDialog()
    dialog.setWindowTitle("Desktop Cat Settings")
    layout = QFormLayout(dialog)

    name_edit = QLineEdit(config.get("name", ""))
    layout.addRow("Name:", name_edit)

    fur_color = {"value": config.get("fur_color")}
    color_button = QPushButton("Choose...")

    def _pick_color():
        current = QColor(*fur_color["value"]) if fur_color["value"] else QColor(242, 166, 90)
        chosen = QColorDialog.getColor(current, dialog, "Fur Color")
        if chosen.isValid():
            fur_color["value"] = [chosen.red(), chosen.green(), chosen.blue()]

    color_button.clicked.connect(_pick_color)
    layout.addRow("Fur color:", color_button)

    pattern_combo = QComboBox()
    pattern_combo.addItems(["solid", "tabby"])
    pattern_combo.setCurrentText(config.get("pattern", "solid"))
    layout.addRow("Pattern:", pattern_combo)

    stretch_check = QCheckBox("Enabled")
    stretch_check.setChecked(config["reminders"]["stretch"]["enabled"])
    stretch_spin = QSpinBox()
    stretch_spin.setRange(1, 480)
    stretch_spin.setValue(config["reminders"]["stretch"]["interval_minutes"])
    layout.addRow("Stretch reminder:", stretch_check)
    layout.addRow("  every (minutes):", stretch_spin)

    water_check = QCheckBox("Enabled")
    water_check.setChecked(config["reminders"]["water"]["enabled"])
    water_spin = QSpinBox()
    water_spin.setRange(1, 480)
    water_spin.setValue(config["reminders"]["water"]["interval_minutes"])
    layout.addRow("Water reminder:", water_check)
    layout.addRow("  every (minutes):", water_spin)

    pinned_edit = QLineEdit(config["reminders"].get("pinned_message", ""))
    layout.addRow("Pinned message:", pinned_edit)

    pomodoro_check = QCheckBox("Enabled")
    pomodoro_check.setChecked(config["pomodoro"]["enabled"])
    focus_spin = QSpinBox()
    focus_spin.setRange(1, 180)
    focus_spin.setValue(config["pomodoro"]["focus_minutes"])
    break_spin = QSpinBox()
    break_spin.setRange(1, 60)
    break_spin.setValue(config["pomodoro"]["break_minutes"])
    layout.addRow("Pomodoro:", pomodoro_check)
    layout.addRow("  focus (minutes):", focus_spin)
    layout.addRow("  break (minutes):", break_spin)

    autostart_check = QCheckBox("Start automatically at login")
    autostart_check.setChecked(autostart.is_enabled())
    layout.addRow(autostart_check)

    buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
    layout.addRow(buttons)

    def _save():
        new_config = {
            "name": name_edit.text(),
            "fur_color": fur_color["value"],
            "pattern": pattern_combo.currentText(),
            "reminders": {
                "stretch": {"enabled": stretch_check.isChecked(), "interval_minutes": stretch_spin.value()},
                "water": {"enabled": water_check.isChecked(), "interval_minutes": water_spin.value()},
                "custom": config["reminders"].get("custom", []),
                "pinned_message": pinned_edit.text(),
            },
            "pomodoro": {
                "enabled": pomodoro_check.isChecked(),
                "focus_minutes": focus_spin.value(),
                "break_minutes": break_spin.value(),
            },
        }
        cat_config.save_config(new_config)
        apply_config(window, new_config)
        autostart.set_enabled(autostart_check.isChecked())
        dialog.accept()

    buttons.accepted.connect(_save)
    buttons.rejected.connect(dialog.reject)

    dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
    dialog.exec()
