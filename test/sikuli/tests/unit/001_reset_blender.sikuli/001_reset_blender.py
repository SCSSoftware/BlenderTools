import configurator, os, shutil
reload(configurator)

configurator.delete_scs_tools_config()

# SETUP SCS TOOLS
p = configurator.start_it_up(getBundlePath(), "startup.blend")
try:
    mouseMove(Location(30,30))
    wait("3d_view_icon.png", 5)
    click(Pattern("3d_view_icon-1.png").similar(0.95))
    click("user_pref_menu_item.png")
    click(Pattern("search.png").similar(0.95))
    type("sc")
    type(Key.ENTER)
    if find(Pattern("addons_scs_tools_entry.png").similar(0.90)).right().exists(Pattern("addon_checkbox_0.png").similar(0.90).targetOffset(15,0)):
        find(Pattern("addons_scs_tools_entry.png").similar(0.90)).right().click(Pattern("addon_checkbox_0.png").similar(0.65).targetOffset(15,0))
    else:
        find(Pattern("addons_scs_tools_entry.png").similar(0.90)).right().click(Pattern("addon_checkbox_1.png").similar(0.95).targetOffset(15,1))
        wait(1)
        find(Pattern("addons_scs_tools_entry.png").similar(0.90)).right().click(Pattern("addon_checkbox_0.png").similar(0.65).targetOffset(15,0))

    find(Pattern("addons_scs_tools_enabled.png").exact())
    click(Pattern("save_user_settings.png").similar(0.95))
    find(Pattern("project_path.png").similar(0.95)).right().click("select_project_path_button.png")
    scs_base = configurator.get_path_property("SCSBasePath")
    find(Pattern("select_scs_project_dir_button.png").similar(0.95)).left().paste(Pattern("empty_input_field.png").similar(0.95), scs_base)
    doubleClick(Pattern("select_scs_project_dir_button-1.png").similar(0.95))
    if find("shader_presets_path_label-1.png").below().exists(Pattern("select_project_path_button.png").similar(0.95)):
        find("shader_presets_path_label-1.png").below().click(Pattern("select_project_path_button.png").similar(0.95))
        blender_path = configurator.get_path_property("SCSToolsPath") + os.sep + "shader_presets.txt"
        find("select_presets_library_file_button-1.png").left().paste(Pattern("empty_input_field.png").similar(0.95), blender_path)
        doubleClick("select_presets_library_file_button-1.png")
    find(Pattern("valid_scs_tools_paths.png").exact())
except:
    configurator.save_screenshot(getBundlePath(), Screen())
    raise
finally:
    configurator.close_blender(p)