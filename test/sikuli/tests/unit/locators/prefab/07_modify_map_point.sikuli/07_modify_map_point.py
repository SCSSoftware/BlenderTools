load("scs_bt_configurator.jar")
import scs_bt_configurator
p = scs_bt_configurator.start_it_up(getBundlePath(), "prefab_locator_map_point.blend")
try:
    mouseMove(Location(0,0)); wait(Pattern("3dview_initial_scene.png").exact(), 5)
    hover(Location(400, 400))  # move cursor above 3D view

    type("g0" + Key.TAB + "3-" + Key.TAB + ".1" + Key.ENTER)  # move locator

    keyDown(Key.SHIFT); type("d"); keyUp(Key.SHIFT)  # copy locator
    type("0" + Key.TAB + "6" + Key.TAB + "0" + Key.ENTER)  # move locator

    keyDown(Key.SHIFT); type("d"); keyUp(Key.SHIFT)  # copy locator
    type("3-" + Key.TAB + "3-" + Key.TAB + "0" + Key.ENTER)  # move locator

    keyDown(Key.SHIFT); type("d"); keyUp(Key.SHIFT)  # copy locator
    type("6" + Key.TAB + "0" + Key.TAB + "0" + Key.ENTER)  # move locator

    keyDown(Key.SHIFT); type("d"); keyUp(Key.SHIFT)  # copy locator
    type("3-" + Key.TAB + "0" + Key.TAB + "0" + Key.ENTER)  # move locator

    keyDown(Key.SHIFT); click(Pattern("3dview_prefab_loc_map_set_1.png").exact().targetOffset(66,-86)); keyUp(Key.SHIFT)  # check for the result in the same time
    click(Pattern("prefab_connect_map_points.png").similar(0.90))
    click(Pattern("3dview_prefab_map_select_01.png").targetOffset(-32,-22))
    keyDown(Key.SHIFT); click(Pattern("3dview_prefab_map_select_02.png").exact().targetOffset(-118,-88)); keyUp(Key.SHIFT)
    click(Pattern("prefab_connect_map_points.png").similar(0.90))
    click(Pattern("3dview_prefab_map_select_03.png").exact().targetOffset(-32,-22))
    keyDown(Key.SHIFT); click(Pattern("3dview_prefab_map_select_04.png").exact().targetOffset(111,91)); keyUp(Key.SHIFT)
    click(Pattern("prefab_connect_map_points.png").similar(0.90))
    click(Pattern("3dview_prefab_map_select_05.png").exact().targetOffset(-32,-20))
    keyDown(Key.SHIFT); click(Pattern("3dview_prefab_map_select_06.png").exact().targetOffset(-189,76)); keyUp(Key.SHIFT)
    click(Pattern("prefab_connect_map_points.png").similar(0.90))
    find(Pattern("3dview_prefab_loc_map_set_2.png").exact())
except:
    scs_bt_configurator.save_screenshot(getBundlePath(), Screen())
    keyUp(Key.SHIFT) # make sure to release shift
    raise
finally:
    scs_bt_configurator.close_blender(p)