import configurator, os
p = configurator.start_it_up(getBundlePath(), "prefab_locator_map_point.blend")
try:
    mouseMove(Location(0,0)); wait("3dview_prefab_loc_map_point.png", 5)
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

    keyDown(Key.SHIFT); rightClick(Pattern("3dview_prefab_loc_map_set_1.png").targetOffset(111,-70)); keyUp(Key.SHIFT)  # check for the result in the same time
    wheel("prefab_map_road_size_1-lane.png", WHEEL_DOWN, 1)  # scroll panels a bit

    click(Pattern("prefab_connect_map_points.png").similar(0.90))
    rightClick("3dview_prefab_map_select_01.png")
    keyDown(Key.SHIFT); rightClick("3dview_prefab_map_select_02.png"); keyUp(Key.SHIFT)
    click(Pattern("prefab_connect_map_points.png").similar(0.90))
    rightClick("3dview_prefab_map_select_03.png")
    keyDown(Key.SHIFT); rightClick("3dview_prefab_map_select_04.png"); keyUp(Key.SHIFT)
    click(Pattern("prefab_connect_map_points.png").similar(0.90))
    rightClick("3dview_prefab_map_select_05.png")
    keyDown(Key.SHIFT); rightClick("3dview_prefab_map_select_06.png"); keyUp(Key.SHIFT)
    click(Pattern("prefab_connect_map_points.png").similar(0.90))
    find("3dview_prefab_loc_map_set_2.png")
except:
    configurator.save_screenshot(getBundlePath(), Screen())
    keyUp(Key.SHIFT) # make sure to release shift
    raise
finally:
    configurator.close_blender(p)