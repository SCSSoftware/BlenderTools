import configurator, os

scs_import_str = " SCS Import"

def go_to_current_dir():
    scs_base = configurator.get_path_property("SCSBasePath")
    find(Pattern("filebrowser_import_button.png").exact()).left().paste(Pattern("empty_input_field.png").exact(), scs_base); type(Key.ENTER)

p = configurator.start_it_up(getBundlePath(), "startup.blend")
try:
    wait(Pattern("3dview_init-1.png").similar(0.90), 5); hover(Pattern("3dview_init-1.png").similar(0.90)); type(Key.ESC)
    click(Pattern("export_selected_button.png").similar(0.90)) 
    find(Pattern("export_panel_preview.png").similar(0.90)); hover(Pattern("3dview_local_view.png").similar(0.90))
    type(Key.ESC); find(Pattern("3dview_init-1.png").similar(0.90))
    click(Pattern("export_selected_button.png").similar(0.90)) 
    find(Pattern("export_panel_preview.png").similar(0.90)); hover(Pattern("3dview_local_view.png").similar(0.90))
    
    type(Key.ENTER);
    wait(0.5); type(Key.ENTER); mouseMove(Location(0,0)); hover(Pattern("3dview_init-1.png").similar(0.90))
    type("3"); click();
    type(scs_import_str + Key.ENTER); go_to_current_dir()
    click(Pattern("import_game_object_001.png").similar(0.90)); type(Key.ENTER); find(Pattern("imported_game_object_001.png").similar(0.90))
    type("4");
    type(scs_import_str + Key.ENTER); go_to_current_dir()
    click(Pattern("import_game_object_002.png").similar(0.90)); type(Key.ENTER); find(Pattern("imported_game_object_002.png").similar(0.90))
except:
    configurator.save_screenshot(getBundlePath(), Screen())
    raise
finally:
    configurator.close_blender(p)