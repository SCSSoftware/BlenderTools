import configurator, subprocess
reload(configurator)
p = configurator.start_it_up(getBundlePath(), "3_Ico_Sphere_2_Materials.blend")
try:
    wait(Pattern("3dview_3_Ico_Sphere_2_Materials.png").similar(0.90), 5); hover(Pattern("3dview_3_Ico_Sphere_2_Materials.png").similar(0.90)); type(Key.ESC)
    click(Pattern("export_scene_button.png").similar(0.90))
    wait(1.5); type(Key.ENTER)
    click(Pattern("second_layer_button.png").exact())
    hover(Location(300, 400))  # move cursor to 3D view
    type(Key.SPACE + "Cursor to Center" + Key.ENTER)
    type(Key.SPACE + "SCS Import" + Key.ENTER)
    scs_base = configurator.get_path_property("SCSBasePath")
    find(Pattern("filebrowser_import_button.png").exact()).left().paste(Pattern("empty_input_field.png").exact(), scs_base)
    type(Key.ENTER)
    click(Pattern("3_ico_sphere_2_materials.png").similar(0.95))
    type(Key.ENTER)
    keyDown(Key.SHIFT); click(Pattern("lamps_layer_button.png").exact()); keyUp(Key.SHIFT)
    click(Pattern("3dview_user_persp.png").similar(0.95))
    find(Pattern("3dview_3_Ico_Sphere_2_Materials_imported_2.png").exact())
except:
    configurator.save_screenshot(getBundlePath(), Screen())
    raise
finally:
    configurator.close_blender(p)