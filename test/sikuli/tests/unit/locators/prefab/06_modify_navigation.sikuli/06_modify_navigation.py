import configurator, os
p = configurator.start_it_up(getBundlePath(), "prefab_locator_navigation.blend")
try:
    mouseMove(Location(0,0)); wait("3dview_prefab_loc_navigation-1.png", 5)
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

    keyDown(Key.SHIFT); rightClick(Pattern("3dview_prefab_nav_select_01-1.png").similar(0.90)); keyUp(Key.SHIFT)
    click(Pattern("prefab_connect_navigation_points.png").similar(0.90))
    rightClick(Pattern("3dview_prefab_nav_select_02.png").similar(0.90))
    keyDown(Key.SHIFT); rightClick(Pattern("3dview_prefab_nav_select_03.png").similar(0.90)); keyUp(Key.SHIFT)
    click(Pattern("prefab_connect_navigation_points.png").similar(0.90))
    rightClick("3dview_prefab_nav_select_04-1.png")
    keyDown(Key.SHIFT); rightClick(Pattern("3dview_prefab_nav_select_05.png").similar(0.90)); keyUp(Key.SHIFT)
    click(Pattern("prefab_connect_navigation_points.png").similar(0.90))
    rightClick(Pattern("3dview_prefab_nav_select_06.png").similar(0.90))
    keyDown(Key.SHIFT); rightClick(Pattern("3dview_prefab_nav_select_07.png").similar(0.90)); keyUp(Key.SHIFT)
    click(Pattern("prefab_connect_navigation_points.png").similar(0.90))
    rightClick(Pattern("3dview_prefab_nav_select_08-1.png").similar(0.90))
    click("prefab_nav_all_vehicles.png")
    click("prefab_nav_trucks_only_pick.png")
    click("prefab_nav_left_blinker.png")
    rightClick(Pattern("3dview_prefab_nav_select_09.png").similar(0.90))
    click("prefab_nav_all_vehicles.png")
    click("prefab_nav_no_trucks_pick.png")
    click("prefab_nav_right_blinker.png")
    find(Pattern("3dview_prefab_nav_set-1.png").similar(0.95))
except:
    configurator.save_screenshot(getBundlePath(), Screen())
    raise
finally:
    configurator.close_blender(p)