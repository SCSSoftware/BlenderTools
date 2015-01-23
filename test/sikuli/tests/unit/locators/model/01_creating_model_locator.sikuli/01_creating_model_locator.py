import configurator, os
p = configurator.start_it_up(getBundlePath(), "startup.blend")
try:
    mouseMove(Location(0,0)); rightClick("3dview_initial_scene.png", 5)
    type(Key.SPACE + "Add Empty")  # search for Add Empty operator
    type(Key.ENTER)  # confirm executing of operator
    type(Key.ENTER)  # confirm creaton of plain axes empty
    find("properties_panel_icon.png").right().click("object_properties_icon.png")
    click("select_object_type.png")
    click("select_object_type_locator.png")
    find("select_object_type_locator.png").below().click("select_locator_type.png")
    click("model.png"); find("3dview_model_loc.png")
    
except:
    configurator.save_screenshot(getBundlePath(), Screen())
    raise
finally:
    configurator.close_blender(p)