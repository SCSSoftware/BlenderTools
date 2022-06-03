load("scs_bt_configurator.jar")
import scs_bt_configurator
p = scs_bt_configurator.start_it_up(getBundlePath(), "prefab_locator_sign.blend")
try:
    mouseMove(Location(0,0)); wait(Pattern("3dview_init_scene.png").exact(), 5)
    hover(Location(450, 400))
    type("g")
    type(".2"); type(Key.TAB)
    type(".5"); type(Key.TAB)
    type(".3"); type(Key.ENTER)
    type(Key.F3); type("add scs root"); type(Key.ENTER)
    click(Pattern("3dview_sign_added_to_root.png").exact().targetOffset(135,-3))
    click("object_properties_icon.png")
    click("prefab_sign_model_select.png"); type("roadsign")
    click("prefab_sign_roadsign_item_select.png")
    find("prefab_sign_roadsign_item_selected.png")
    click("parts_panel_expand.png")
    find(Pattern("default_part_item_list.png").exact())
except:
    scs_bt_configurator.save_screenshot(getBundlePath(), Screen())
    raise
finally:
    scs_bt_configurator.close_blender(p)