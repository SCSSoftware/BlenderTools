load("scs_bt_configurator.jar")
import scs_bt_configurator
p = scs_bt_configurator.start_it_up(getBundlePath(), "5_locators_model.blend")
try:
    wait(Pattern("3dview_start.png").exact(), 5); hover(Pattern("3dview_start.png").exact()); type(Key.ESC)
    click(Pattern("export_scene_button.png").exact())
    wait("3dview_start.png", 5);  # no warnings should appear !
    hover(Location(300, 400))  # move cursor to 3D view
    type(Key.ESC); wait(0.5); type(Key.ESC)  # hide warnings
    type("2")  # switch to 2nd collection
    type(Key.F3 + "SCS Import" + Key.ENTER)  # do import
    hover(Pattern("new_folder_button.png").exact()); mouseMove(50, 0); paste(scs_bt_configurator.get_path_property("SCSBasePath"))
    wait(0.1); click(Pattern("5_locators_model_pim.png").similar(0.95)); type(Key.ENTER)
    wait(0.5); click(Pattern("3dview_imported.png").exact().targetOffset(177,-162))
    click(Pattern("object_tab.png").similar(0.95))
    wait(Pattern("flare_lamp_hookup.png").exact(), 1)
except:
    scs_bt_configurator.save_screenshot(getBundlePath(), Screen())
    raise
finally:
    scs_bt_configurator.close_blender(p)
