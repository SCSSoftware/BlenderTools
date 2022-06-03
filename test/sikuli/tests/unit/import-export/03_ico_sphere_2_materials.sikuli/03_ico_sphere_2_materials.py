load("scs_bt_configurator.jar")
import scs_bt_configurator
p = scs_bt_configurator.start_it_up(getBundlePath(), "3_Ico_Sphere_2_Materials.blend")
try:
    wait(Pattern("3dview_3_Ico_Sphere_2_Materials.png").exact(), 5); hover(Pattern("3dview_3_Ico_Sphere_2_Materials.png").similar(0.90)); type(Key.ESC)
    click(Pattern("export_scene_button.png").exact())
    wait(Pattern("3dview_3_Ico_Sphere_2_Materials.png").exact(), 5);  # no warnings should appear !
    hover(Location(300, 400))  # move cursor to 3D view
    type(Key.ESC); wait(0.5); type(Key.ESC)  # hide warnings
    type("2")  # switch to 2nd collection
    type(Key.F3 + "SCS Import" + Key.ENTER)  # do import
    hover(Pattern("new_folder_button.png").exact()); mouseMove(50, 0); paste(scs_bt_configurator.get_path_property("SCSBasePath"))
    wait(0.1); click(Pattern("3_ico_sphere_2_materials.png").similar(0.95)); type(Key.ENTER)
    wait(Pattern("3dview_3_Ico_Sphere_2_Materials.png").exact(), 5)
except:
    scs_bt_configurator.save_screenshot(getBundlePath(), Screen())
    raise
finally:
    scs_bt_configurator.close_blender(p)