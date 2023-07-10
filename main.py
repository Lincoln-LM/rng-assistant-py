"""Main Application"""

import dearpygui.dearpygui as dpg

from core.util import get_pid_list
from core.instance import gbarng as instance

def hook_callback():
    """Hook into the selected process"""
    pid = int(dpg.get_value(pid_dropdown).split("(")[-1][:-1])
    instance.hook.hook(pid)

def refresh_callback():
    """Refresh process list"""
    dpg.configure_item(pid_dropdown, items=get_pid_list(instance.KEY_WORD))

dpg.create_context()
dpg.create_viewport(title="RNG Assistant", width=800, height=600, vsync=False)
dpg.setup_dearpygui()

with dpg.window(tag="Settings"):
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
