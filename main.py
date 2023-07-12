"""Main Application"""

import tkinter as tk
from tkinter import filedialog
import logging

import dearpygui.dearpygui as dpg
import mem_edit

from core.util import get_pid_list
from core.instance.gbarng import GBA as Instance
from core.exceptions import AddressOutOfRange

instance: Instance = None
windows = ()

def file_callback():
    """Select ROM file"""
    # TODO: axe globals
    global instance, windows
    # needed for filedialog
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename()
    dpg.set_value(file_label, file_path)
    instance = Instance(file_path)
    windows = instance.get_windows()

def hook_callback():
    """Hook into the selected process"""
    global instance

    pid = int(dpg.get_value(pid_dropdown).split("(")[-1][:-1])
    instance.hook.hook(pid)

def refresh_callback():
    """Refresh process list"""
    dpg.configure_item(pid_dropdown, items=get_pid_list(Instance.KEY_WORD))

dpg.create_context()
dpg.create_viewport(title="RNG Assistant", width=800, height=600, vsync=False)
dpg.setup_dearpygui()

with dpg.window(tag="Settings"):
    file_label = dpg.add_text("No Rom Selected...")
    file_selector = dpg.add_button(label="Select Rom", callback=file_callback)
    pid_dropdown = dpg.add_combo(get_pid_list(Instance.KEY_WORD))
    hook_button = dpg.add_button(label="Hook", callback=hook_callback)
    refresh_button = dpg.add_button(label="Refresh", callback=refresh_callback)


dpg.show_viewport()
dpg.set_primary_window("Settings", True)
while dpg.is_dearpygui_running():
    if instance is not None:
        if instance.hook.is_initialized:
            try:
                for window_update in windows:
                    window_update()
            except (AddressOutOfRange,) as error:
                logging.error(error)
            except (mem_edit.utils.MemEditError, OSError) as error:
                logging.error(error)
                instance.hook.detach()
    dpg.render_dearpygui_frame()

dpg.destroy_context()
