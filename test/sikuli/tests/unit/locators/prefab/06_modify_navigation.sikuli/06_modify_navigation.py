load("scs_bt_configurator.jar")

def slowDoubleClick(pattern):
    click(pattern); wait(0.1); click()

import scs_bt_configurator
p = scs_bt_configurator.start_it_up(getBundlePath(), "prefab_locator_navigation.blend")
try:
    mouseMove(Location(0,0)); wait(Pattern("3dview_initial_scene.png").exact(), 5)
    hover(Location(400, 400))  # move cursor abowe 3D view

    type("g0" + Key.TAB + "0" + Key.TAB + ".1" + Key.ENTER)  # move locator

    keyDown(Key.SHIFT); type("d"); keyUp(Key.SHIFT)  # copy locator
    type("1" + Key.TAB + "3" + Key.TAB + "0" + Key.ENTER)  # move locator

    keyDown(Key.SHIFT); type("d"); keyUp(Key.SHIFT)  # copy locator
    type("2-" + Key.TAB + "2" + Key.TAB + "0" + Key.ENTER)  # move locator
    type("rz90" + Key.ENTER)  # rotate locator

    keyDown(Key.SHIFT); type("d"); keyUp(Key.SHIFT)  # copy locator
    type("0" + Key.TAB + "3-" + Key.TAB + "0" + Key.ENTER)  # move locator
    type("rz90-" + Key.ENTER)

    keyDown(Key.SHIFT); type("d"); keyUp(Key.SHIFT)  # copy locator
    type("2" + Key.TAB + "4" + Key.TAB + "0" + Key.ENTER)  # move locator

    keyDown(Key.SHIFT); type("d"); keyUp(Key.SHIFT)  # copy locator
    type("2-" + Key.TAB + "6-" + Key.TAB + "0" + Key.ENTER)  # move locator

    keyDown(Key.SHIFT); click(Pattern("3dview_locators_created.png").exact().targetOffset(-62,-12)); keyUp(Key.SHIFT)
    click(Pattern("prefab_connect_navigation_points.png").similar(0.90))
    slowDoubleClick(Pattern("3dview_prefab_nav_select_02.png").exact().targetOffset(-62,-12))
    keyDown(Key.SHIFT); click(Pattern("3dview_prefab_nav_select_03.png").exact().targetOffset(114,-60)); keyUp(Key.SHIFT)
    click(Pattern("prefab_connect_navigation_points.png").similar(0.90))
    slowDoubleClick(Pattern("3dview_prefab_nav_select_04.png").exact().targetOffset(-106,91))
    keyDown(Key.SHIFT); click(Pattern("3dview_prefab_nav_select_05.png").exact().targetOffset(54,6)); keyUp(Key.SHIFT)
    click(Pattern("prefab_connect_navigation_points.png").similar(0.90))
    slowDoubleClick(Pattern("3dview_prefab_nav_select_06.png").exact().targetOffset(52,8))
    keyDown(Key.SHIFT); click(Pattern("3dview_prefab_nav_select_07.png").exact().targetOffset(22,-70)); keyUp(Key.SHIFT)
    click(Pattern("prefab_connect_navigation_points.png").similar(0.90))
    click(Pattern("3dview_prefab_nav_select_08.png").exact().targetOffset(53,8))
    click("prefab_nav_all_vehicles.png")
    click("prefab_nav_trucks_only_pick.png")
    click("prefab_nav_left_blinker.png")
    click(Pattern("3dview_prefab_nav_select_09.png").exact().targetOffset(-58,-10))
    click("prefab_nav_all_vehicles.png")
    click("prefab_nav_no_trucks_pick.png")
    click("prefab_nav_right_blinker.png")
    find(Pattern("3dview_prefab_nav_set-1.png").exact())
except:
    scs_bt_configurator.save_screenshot(getBundlePath(), Screen())
    keyUp(Key.SHIFT) # make sure to release shift
    raise
finally:
    scs_bt_configurator.close_blender(p)