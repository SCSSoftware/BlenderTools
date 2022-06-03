load("scs_bt_configurator.jar")
import scs_bt_configurator
p = scs_bt_configurator.start_it_up(getBundlePath(), "model_locator.blend", delete_pix=False)
try:
    mouseMove(Location(0,0)); wait(Pattern("3dview_model_loc.png").exact(), 5)
    pm_header_reg = find("model_preview_panel_header.png")
    pm_header_reg.below().click(Pattern("model_preview_file_select.png").targetOffset(77,1))
    click("model_preview_file_selected.png"); type(Key.ENTER); find(Pattern("3dview_model_loc_preview_sign_wire.png").exact())
    pm_header_reg.below().click("model_preview_model_draw-1.png")
    pm_header_reg.below().click("model_preview_model_draw_solid.png"); find(Pattern("3dview_model_loc_preview_sign_solid.png").exact())
    click(Pattern("model_preview_panel_header.png").exact().targetOffset(-85,0)); find(Pattern("3dview_model_loc.png").exact())
    click(atMouse())
    find(Pattern("3dview_model_loc_preview_sign_solid.png").exact())
    click("workspace_settings_tab.png"); mouseMove(60, 60); wheel(WHEEL_DOWN, 6)
    click("model_preview_show_preview_3.png"); find(Pattern("3dview_model_loc.png").exact())
    click(atMouse())
    find(Pattern("3dview_model_loc_preview_sign_solid.png").exact())
    click("object_tab.png")
    click("model_preview_model_draw_1-1.png")
    click("model_preview_model_draw_wire.png"); find(Pattern("3dview_model_loc_preview_sign_wire.png").exact())
except:
    scs_bt_configurator.save_screenshot(getBundlePath(), Screen())
    raise
finally:
    scs_bt_configurator.close_blender(p)