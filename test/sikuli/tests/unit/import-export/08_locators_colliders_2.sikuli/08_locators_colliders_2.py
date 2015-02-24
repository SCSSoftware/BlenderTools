import configurator, subprocess
reload(configurator)
p = configurator.start_it_up(getBundlePath(), "8_locators_collision_rotated.blend")
try:
    wait(Pattern("3dview_8_locators_collision_rotated.png").similar(0.90), 5); hover(Pattern("3dview_8_locators_collision_rotated.png").similar(0.90)); type(Key.ESC)
    click(Pattern("export_scene_button.png").similar(0.90))
    wait(1.5); type(Key.ENTER)
    click(Pattern("second_layer_button.png").exact())
    hover(Location(300, 400))  # move cursor to 3D view
    type(Key.SPACE + "SCS Import" + Key.ENTER)
    scs_base = configurator.get_path_property("SCSBasePath")
    find(Pattern("filebrowser_import_button.png").exact()).left().paste(Pattern("empty_input_field.png").exact(), scs_base)
    type(Key.ENTER)
    click(Pattern("8_locators_collision_rotated.png").similar(0.95))
    type(Key.ENTER)
    find(Pattern("3dview_8_locators_collision_rotated.png").similar(0.91))
except:
    configurator.save_screenshot(getBundlePath(), Screen())
    raise
finally:
    configurator.close_blender(p)
