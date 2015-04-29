import configurator, subprocess
reload(configurator)
p = configurator.start_it_up(getBundlePath(), "looks.blend")

try:
    wait(Pattern("3dview_first_look.png").similar(0.95),5)
    click(Pattern("looks_entries.png").similar(0.92).targetOffset(-3,10)); wait(Pattern("3dview_second_look.png").similar(0.91))
    click(Pattern("export_selected_button.png").similar(0.91));
    wait(1); type(Key.ESC)
    hover(Pattern("3dview_second_look.png").similar(0.91)); type("2")
    type(Key.SPACE + "SCS Import"); type(Key.ENTER)
    scs_base = configurator.get_path_property("SCSBasePath")
    find(Pattern("filebrowser_import_button.png").exact()).left().paste(Pattern("empty_input_field.png").exact(), scs_base)
    type(Key.ENTER)
    click("game_object_file.png")
    type(Key.ENTER)
    wait(Pattern("3dview_first_look.png").similar(0.95))
    click(Pattern("looks_entries.png").similar(0.92).targetOffset(-3,10));
    wait(Pattern("3dview_second_look.png").similar(0.91))
except:
    configurator.save_screenshot(getBundlePath(), Screen())
    raise
finally:
    configurator.close_blender(p)