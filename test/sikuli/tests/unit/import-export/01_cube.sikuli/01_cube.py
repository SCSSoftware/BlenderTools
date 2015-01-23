import configurator, os
p = configurator.start_it_up(getBundlePath(), "Default_Scene_with_Cube.blend")
try:
    wait(Pattern("startup_screen.png").similar(0.90), 5); type(Key.ESC); hover(Pattern("startup_screen.png").similar(0.90)); type(Key.ESC)
    click(Pattern("export_scene_button.png").similar(0.90))
    wait(1.5)
    click(Pattern("second_layer_button.png").exact())
    hover(Location(300, 400))  # move cursor to 3D view
    type(Key.SPACE + "SCS Import" + Key.ENTER)
    find(Pattern("filebrowser_import_button.png").exact()).left().paste(Pattern("empty_input_field.png").exact(), getBundlePath())
    type(Key.ENTER)
    click(Pattern("scene_with_cube_file.png").exact())
    type(Key.ENTER)
    find(Pattern("import_cube_result.png").similar(0.90))
except:
    configurator.save_screenshot(getBundlePath(), Screen())
    raise
finally:
    configurator.close_blender(p)
