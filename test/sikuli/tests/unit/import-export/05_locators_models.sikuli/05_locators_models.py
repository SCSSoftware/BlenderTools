import configurator, subprocess
reload(configurator)
p = configurator.start_it_up(getBundlePath(), "5_locators_model.blend")
try:
    wait(Pattern("3dview_start.png").similar(0.95), 5); hover(Pattern("3dview_start.png").similar(0.95)); type(Key.ESC)
    click(Pattern("export_scene_button.png").similar(0.90))
    wait(1)
    click(Pattern("second_layer_button.png").exact())
    hover(Location(300, 400))  # move cursor to 3D view
    type(Key.SPACE + "SCS Import" + Key.ENTER)
    scs_base = configurator.get_path_property("SCSBasePath")
    find(Pattern("filebrowser_import_button.png").exact()).left().paste(Pattern("empty_input_field.png").exact(), scs_base)
    type(Key.ENTER)
    click(Pattern("5_locators_model.png").similar(0.95))
    type(Key.ENTER)
    click(Pattern("3dview_user_persp.png").similar(0.95)); type("a")
    rightClick(Pattern("3dview_imported.png").similar(0.89).targetOffset(-42,-154))
    click(Pattern("object_tab.png").similar(0.95))
    
    find(Pattern("flare_lamp_hookup.png").similar(0.95))
except:
    configurator.save_screenshot(getBundlePath(), Screen())
    raise
finally:
    configurator.close_blender(p)
