load("scs_bt_configurator.jar")
import scs_bt_configurator

scs_bt_configurator.delete_scs_tools_config()

# SETUP SCS TOOLS
p = scs_bt_configurator.start_it_up(getBundlePath(), "startup.blend")
try:
    mouseMove(Location(100,100))
    wait("3d_view_icon.png", 10)
    click(Pattern("3d_view_icon-1.png").similar(0.95).targetOffset(-15,8))
    click("user_pref_menu_item.png")
    click("addons_button.png")
    click(Pattern("search.png").similar(0.95))
    type("scs" + Key.ENTER)
    if exists(Pattern("addons_scs_tools_enabled.png").exact(), 0.5):
        click(Pattern("addons_scs_tools_enabled.png").exact().targetOffset(-56,0))
        wait(1)
        find(Pattern("addons_scs_tools_entry.png").exact()).left().click(Pattern("addon_checkbox_0.png").exact().targetOffset(15,0))
    else:
        find(Pattern("addons_scs_tools_entry.png").exact()).left().click(Pattern("addon_checkbox_0.png").exact().targetOffset(11,0))
    mouseMove(0, 50)
    find(Pattern("addons_scs_tools_enabled.png").exact())
    click("interface_button.png")
    if exists(Pattern("developer_extras_prop.png").exact(), 0.5):
        click(Pattern("developer_extras_prop.png").exact())
    click("preferences_menu.png", 1)
    click(Pattern("save_user_settings.png").similar(0.95))

    # SCS PROJECT BASE PATH

    find(Pattern("project_path.png").similar(0.95)).right().click("select_project_path_button.png")
    wait(1)
    new_folder_loc = find("new_folder_button.png")
    new_folder_loc.x += 50
    click(new_folder_loc)
    paste(scs_bt_configurator.get_path_property("SCSBasePath"))
    doubleClick("select_scs_project_dir_button.png")

    # SHADER PRESETS PATH

    shader_preset_pos = wait(Pattern("shader_presets_path_label-1.png").exact(), 10)
    shader_preset_pos.below().click(Pattern("enable_custom_shader_presets_path.png").targetOffset(-12,0))
    shader_preset_pos.right().below().click(Pattern("select_project_path_button.png").similar(0.95))
    wait(1)
    new_folder_loc = find("new_folder_button.png")
    new_folder_loc.x += 50
    click(new_folder_loc)
    paste(scs_bt_configurator.get_path_property("SCSToolsPath") + "/" + "shader_presets.txt")
    doubleClick(Pattern("select_presets_library_file_button-1.png").similar(0.90))

    # FINAL CHECK WHERE PATHS SHOULD BE PROPERLY SET

    mouseMove(Location(300, 300));  # move mouse away from properties panel 
    wait(Pattern("valid_scs_tools_paths.png").exact(), 10)
except:
    scs_bt_configurator.save_screenshot(getBundlePath(), Screen())
    raise
finally:
    scs_bt_configurator.close_blender(p)