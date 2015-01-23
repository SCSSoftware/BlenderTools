import configurator, subprocess
reload(configurator)
p = configurator.start_it_up(getBundlePath(), "4_locators_collision.blend")
try:
    wait(Pattern("3dview_4_locators_collision.png").similar(0.90), 5); hover(Pattern("3dview_4_locators_collision.png").similar(0.90)); type(Key.ESC)
    click(Pattern("export_scene_button.png").similar(0.90))
    wait(3)
    click(Pattern("second_layer_button.png").exact())
    hover(Location(300, 400))  # move cursor to 3D view
    type(Key.SPACE + "SCS Import" + Key.ENTER)
    find(Pattern("filebrowser_import_button.png").exact()).left().paste(Pattern("empty_input_field.png").exact(), getBundlePath())
    type(Key.ENTER)
    click(Pattern("4_locators_collision.png").similar(0.95))
    type(Key.ENTER)
    find(Pattern("3dview_4_locators_collision_imported_1.png").similar(0.95))
except:
    configurator.save_screenshot(getBundlePath(), Screen())
    raise
finally:
    configurator.close_blender(p)
