load("scs_bt_configurator.jar")
import scs_bt_configurator

def go_to_current_dir():
    type(Key.F3 + " SCS Import" + Key.ENTER);
    scs_base = scs_bt_configurator.get_path_property("SCSBasePath")
    hover(Pattern("new_folder_button.png").exact()); mouseMove(50, 0); paste(scs_base)

p = scs_bt_configurator.start_it_up(getBundlePath(), "startup.blend")
try:
    wait(Pattern("3dview_init.png").exact(), 5); hover(Pattern("3dview_init.png").exact()); type(Key.ESC)
    click("export_selected_button.png")
    wait(Pattern("export_panel_preview.png").exact(), 2); hover(Pattern("3dview_local_view.png").exact())
    type(Key.ESC); wait(Pattern("3dview_init.png").exact(), 2)
    click(Pattern("export_selected_button.png").similar(0.90))
    wait(Pattern("export_panel_preview.png").exact(), 2); hover(Pattern("3dview_local_view.png").exact())

    type(Key.ENTER);
    wait(Pattern("3dview_init.png").exact(), 2); hover(Pattern("3dview_init.png").exact())
    type("3"); go_to_current_dir()
    click(Pattern("game_object_001_pim.png").similar(0.95)); type(Key.ENTER); wait(Pattern("imported_game_object_001.png").similar(0.90), 5)
    type("4"); go_to_current_dir()
    click(Pattern("game_object_002_pim.png").similar(0.95)); type(Key.ENTER); wait(Pattern("imported_game_object_002.png").similar(0.90), 5)
except:
    scs_bt_configurator.save_screenshot(getBundlePath(), Screen())
    raise
finally:
    scs_bt_configurator.close_blender(p)