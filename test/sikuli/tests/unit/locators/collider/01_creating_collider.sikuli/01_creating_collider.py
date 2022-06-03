load("scs_bt_configurator.jar")
import scs_bt_configurator
p = scs_bt_configurator.start_it_up(getBundlePath(), "startup.blend")
try:
    wait(Pattern("empty_startup.png").exact(), 5); hover(Pattern("empty_startup.png").exact());
    type(Key.F3 + "Add Empty")  # search for Add Empty operator
    type(Key.ENTER)  # confirm executing of operator
    type(Key.ENTER)  # confirm creaton of plain axes empty
    find("properties_panel_icon.png").below().click("object_properties_icon.png")
    click("select_object_type.png")
    click("select_object_type_locator.png")
    find("select_object_type_locator.png").below().click("select_locator_type.png")
    click("select_locator_type_collision.png")
    find(Pattern("3dview_locator_collision.png").exact())
except:
    scs_bt_configurator.save_screenshot(getBundlePath(), Screen())
    raise
finally:
    scs_bt_configurator.close_blender(p)