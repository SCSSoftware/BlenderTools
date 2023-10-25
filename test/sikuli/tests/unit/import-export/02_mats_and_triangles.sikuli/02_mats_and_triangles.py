load("scs_bt_configurator.jar")
import scs_bt_configurator
p = scs_bt_configurator.start_it_up(getBundlePath(), "2_Triangles_2_Materials.blend")
try:
    mouseMove(Location(0,0))
    wait(Pattern("2_materials_and_triangles_startup.png").similar(0.96), 5); hover(Pattern("2_materials_and_triangles_startup.png").similar(0.96)); type(Key.ESC)
    export_region = find("export_buttons_region.png")
    export_region.click("export_selection_button.png")
    export_region.click(Pattern("preview_selection_button.png").exact().targetOffset(-37,0))
    mouseMove(0, 20)  # move away from the checkbox
    export_region.find(Pattern("preview_selection_button_1.png").exact())
    export_region.click(Pattern("export_button.png").exact())
    wait(Pattern("2_materials_and_triangles_startup.png").exact(), 5);  # no warnings should appear!
    hover(Location(300, 400))  # move cursor to 3D view
    type("2")  # switch to 2nd collection
    type(Key.F3 + "SCS Import" + Key.ENTER)  # do import
    hover(Pattern("new_folder_button.png").exact()); mouseMove(50, 0); paste(scs_bt_configurator.get_path_property("SCSBasePath"))
    wait(0.1); click(Pattern("2_trinagles_materials_pim.png").similar(0.96)); type(Key.ENTER)
    wait(Pattern("2_materials_and_triangles_after_import.png").similar(0.98), 6)
except:
    scs_bt_configurator.save_screenshot(getBundlePath(), Screen())
    raise
finally:
    scs_bt_configurator.close_blender(p)