load("scs_bt_configurator.jar")
import scs_bt_configurator
p = scs_bt_configurator.start_it_up(getBundlePath(), "6_locators_prefab.blend")
try:
    wait(Pattern("3dview_6_locators_prefab.png").exact(), 5); hover(Pattern("3dview_6_locators_prefab.png").exact()); type(Key.ESC)
    click("export_scene_button.png")
    wait(Pattern("3dview_6_locators_prefab.png").exact(), 5);  # no warnings should appear!
    hover(Location(300, 400))  # move cursor to 3D view
    type(Key.ESC); wait(0.5); type(Key.ESC)  # hide warnings
    type("2")  # switch to 2nd collection
    type(Key.F3 + "SCS Import" + Key.ENTER)  # do import
    hover(Pattern("new_folder_button.png").exact()); mouseMove(50, 0); paste(scs_bt_configurator.get_path_property("SCSBasePath"))
    wait(0.1); click(Pattern("6_locators_prefab_pim.png").similar(0.95)); type(Key.ENTER)
    wait(Pattern("3dview_6_locators_prefab_imported.png").exact(), 5)
except:
    scs_bt_configurator.save_screenshot(getBundlePath(), Screen())
    raise
finally:
    scs_bt_configurator.close_blender(p)
