import configurator, os
p = configurator.start_it_up(getBundlePath(), "model_locator.blend", delete_pix=False)
try:
    mouseMove(Location(0,0)); wait("3dview_model_loc.png", 5)
    find("model_preview-1.png").right().click("model_preview_file_select.png")
    click("model_preview_file_selected.png"); type(Key.ENTER); find("3dview_model_loc_preview_sign_wire.png")
    click("model_preview_model_draw-1.png")
    click("model_preview_model_draw_solid.png")
    find("3dview_model_loc_preview_sign_solid.png")
    click("model_preview_show_preview.png"); find("3dview_model_loc_no_preview.png")
    click(atMouse())
    find("3dview_model_preview_model_solid-1.png")
    click("scene_tab.png")
    click("model_preview_show_preview_3.png"); find("3dview_model_preview_model_off-1.png")
    click(atMouse())
    find("3dview_model_preview_model_solid-1.png")
    click("object_tab.png")
    click("model_preview_model_draw_1-1.png")
    click("model_preview_model_draw_wire.png"); find("3dview_model_loc_no_preview.png")
except:
    configurator.save_screenshot(getBundlePath(), Screen())
    raise
finally:
    configurator.close_blender(p)