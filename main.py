"""Main Application"""

import tkinter as tk
from tkinter import filedialog
import logging

import dearpygui.dearpygui as dpg

from core.util import get_pid_list
from core.instance import gbarng as instance

def file_callback():
    """Select ROM file"""
    # needed for filedialog
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename()
    dpg.set_value(file_label, file_path)

def hook_callback():
    """Hook into the selected process"""
    rom_file = dpg.get_value(file_label)
    if rom_file == "No Rom Selected...":
        logging.error("No rom selected.")
    pid = int(dpg.get_value(pid_dropdown).split("(")[-1][:-1])
    instance.hook.hook(pid, rom_file)

def refresh_callback():
    """Refresh process list"""
    dpg.configure_item(pid_dropdown, items=get_pid_list(instance.KEY_WORD))

dpg.create_context()
dpg.create_viewport(title="RNG Assistant", width=800, height=600, vsync=False)
dpg.setup_dearpygui()

with dpg.window(tag="Settings"):
    file_label = dpg.add_text("No Rom Selected...")
    file_selector = dpg.add_button(label="Select Rom", callback=file_callback)
    pid_dropdown = dpg.add_combo(get_pid_list(instance.KEY_WORD))
    hook_button = dpg.add_button(label="Hook", callback=hook_callback)
    refresh_button = dpg.add_button(label="Refresh", callback=refresh_callback)

windows = instance.get_windows()

dpg.show_viewport()
dpg.set_primary_window("Settings", True)
while dpg.is_dearpygui_running():
    if instance.hook.is_initialized:
        for window_update in windows:
            window_update()
    dpg.render_dearpygui_frame()

dpg.destroy_context()
