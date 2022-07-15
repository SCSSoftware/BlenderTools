load("scs_bt_configurator.jar")
import scs_bt_configurator
p = scs_bt_configurator.start_it_up(getBundlePath(), "Default_Scene_with_Cube.blend")
try:
    wait(Pattern("startup_screen.png").exact(), 5); type(Key.ESC); hover(Pattern("startup_screen.png").exact()); type(Key.ESC)
    keyDown(Key.SHIFT); type(Key.RIGHT); keyUp(Key.SHIFT);
    find(Pattern("startup_screen_last_frame.png").exact())
    click("export_scene_button.png")
    wait(1.5)
    hover(Location(300, 400))  # move cursor to 3D view
    type(2 * Key.ESC)  # hide warnings
    type("2")  # switch to 2nd collection
    type(Key.F3 + "SCS Import" + Key.ENTER)  # do import
    hover(Pattern("new_folder_button.png").exact()); mouseMove(50, 0); paste(scs_bt_configurator.get_path_property("SCSBasePath"))
    wait(0.1); click(Pattern("scene_with_cube_file.png").similar(0.95)); type(Key.ENTER)
    find(Pattern("after_import_screen.png").exact())
    keyDown(Key.SHIFT); type(Key.RIGHT); keyUp(Key.SHIFT);
    find(Pattern("after_import_screen_last_frame.png").exact())
except:
    scs_bt_configurator.save_screenshot(getBundlePath(), Screen())
    raise
finally:
    scs_bt_configurator.close_blender(p)
