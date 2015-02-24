import configurator, subprocess
reload(configurator)
p = configurator.start_it_up(getBundlePath(), "2_Triangles_2_Materials.blend")
try:
    mouseMove(Location(0,0))
    wait(Pattern("2_materials_and_triangles_startup.png").similar(0.80), 5); hover(Pattern("2_materials_and_triangles_startup.png").similar(0.80)); type(Key.ESC)
    type("aa")  # deselect and select all
    click(Pattern("preview_selection_button.png").similar(0.90))
    click(Pattern("export_selected_button.png").similar(0.90))
    wait(1); type(Key.ENTER)
    click(Pattern("second_layer_button.png").exact())
    hover(Location(300, 400))  # move cursor to 3D view
    type(Key.SPACE + "SCS Import" + Key.ENTER)
    scs_base = configurator.get_path_property("SCSBasePath")
    find(Pattern("filebrowser_import_button.png").exact()).left().paste(Pattern("empty_input_field.png").exact(), scs_base)
    type(Key.ENTER)
    wait(0.1); click(Pattern("2_trinagles_materials_pim.png").similar(0.95))
    type(Key.ENTER)
    find(Pattern("2_triangles_materials_after_import.png").similar(0.80))
except:
    configurator.save_screenshot(getBundlePath(), Screen())
    raise
finally:
    configurator.close_blender(p)