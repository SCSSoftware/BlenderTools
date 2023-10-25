load("scs_bt_configurator.jar")

def slowDoubleClick(pattern):
    click(pattern); wait(0.15); click()

import scs_bt_configurator
p = scs_bt_configurator.start_it_up(getBundlePath(), "prefab_locator_trigger.blend")
try:
    wait(Pattern("3dview_initial_scene.png").exact(), 5)
    hover(Location(300, 500))  # move cursor above 3D view

    type("g0" + Key.TAB + "0" + Key.TAB + ".1" + Key.ENTER)  # move locator

    keyDown(Key.SHIFT); type("d"); keyUp(Key.SHIFT)  # copy locator
    type("1" + Key.TAB + "2" + Key.TAB + "0" + Key.ENTER)  # move locator

    keyDown(Key.SHIFT); type("d"); keyUp(Key.SHIFT)  # copy locator
    type("2-" + Key.TAB + "0" + Key.TAB + "0" + Key.ENTER)  # move locator

    slowDoubleClick(Pattern("3dview_prefab_trigger_select_01.png").exact().targetOffset(-86,55))
    keyDown(Key.SHIFT); click(Pattern("3dview_prefab_trigger_select_02.png").exact().targetOffset(104,14)); keyUp(Key.SHIFT)
    click("prefab_connect_trigger_points.png")
    slowDoubleClick(Pattern("3dview_prefab_trigger_select_03.png").exact().targetOffset(102,16))
    keyDown(Key.SHIFT); click(Pattern("3dview_prefab_trigger_select_04.png").exact().targetOffset(-14,-58)); keyUp(Key.SHIFT)
    click("prefab_connect_trigger_points.png")
    slowDoubleClick(Pattern("3dview_prefab_trigger_select_05.png").exact().targetOffset(-14,-56))
    keyDown(Key.SHIFT); click(Pattern("3dview_prefab_trigger_select_06.png").exact().targetOffset(-84,58)); keyUp(Key.SHIFT)
    click("prefab_connect_trigger_points.png")
    slowDoubleClick(Pattern("3dview_prefab_loc_trigger_set_2.png").exact().targetOffset(-82,58))  # check the result in the same time
    click(Pattern("prefab_trigger_range.png").exact()); type("1.5" + Key.ENTER)
    click(Pattern("prefab_trigger_sphere_prop.png").exact())
    click(Pattern("3dview_prefab_trigger_select_07.png").exact().targetOffset(102,12))
    click(Pattern("prefab_trigger_range.png").exact()); type("1" + Key.ENTER)
    click(Pattern("prefab_trigger_sphere_prop.png").exact())
    click(Pattern("3dview_prefab_trigger_select_08.png").exact().targetOffset(-16,-60))
    click(Pattern("prefab_trigger_range.png").exact()); type("0.8" + Key.ENTER)
    click(Pattern("prefab_trigger_sphere_prop.png").exact())
    find(Pattern("3dview_prefab_loc_trigger_set_3.png").exact())
except:
    scs_bt_configurator.save_screenshot(getBundlePath(), Screen())
    raise
finally:
    scs_bt_configurator.close_blender(p)