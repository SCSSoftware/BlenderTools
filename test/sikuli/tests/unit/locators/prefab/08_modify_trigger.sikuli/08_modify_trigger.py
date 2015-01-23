import configurator, os
p = configurator.start_it_up(getBundlePath(), "prefab_locator_trigger.blend")
try:
    click(Pattern("3dview_user_persp.png").similar(0.90))  # get rid of 3D cursor
    wait("3dview_prefab_loc_trigger.png", 5)
    hover(Location(400, 400))  # move cursor above 3D view

    type("g0" + Key.TAB + "0" + Key.TAB + ".1" + Key.ENTER)  # move locator

    keyDown(Key.SHIFT); type("d"); keyUp(Key.SHIFT)  # copy locator
    type("1" + Key.TAB + "2" + Key.TAB + "0" + Key.ENTER)  # move locator

    keyDown(Key.SHIFT); type("d"); keyUp(Key.SHIFT)  # copy locator
    type("2-" + Key.TAB + "0" + Key.TAB + "0" + Key.ENTER)  # move locator

    rightClick(Pattern("3dview_prefab_trigger_select_01-1.png").similar(0.90))
    keyDown(Key.SHIFT); rightClick(Pattern("3dview_prefab_trigger_select_02.png").similar(0.90).targetOffset(54,-39)); keyUp(Key.SHIFT)
    click("prefab_connect_trigger_points.png")
    rightClick(Pattern("3dview_prefab_trigger_select_03.png").similar(0.90).targetOffset(63,-40))
    keyDown(Key.SHIFT); rightClick(Pattern("3dview_prefab_trigger_select_04.png").similar(0.90).targetOffset(8,-41)); keyUp(Key.SHIFT)
    click("prefab_connect_map_points.png")
    find(Pattern("3dview_prefab_loc_trigger_set_1.png").similar(0.90))  # check the result
    rightClick(Pattern("3dview_prefab_trigger_select_05.png").similar(0.90).targetOffset(8,-41))
    keyDown(Key.SHIFT); rightClick(Pattern("3dview_prefab_trigger_select_06.png").similar(0.90).targetOffset(-56,1)); keyUp(Key.SHIFT)
    click("prefab_connect_map_points.png")
    rightClick(Pattern("3dview_prefab_loc_trigger_set_2.png").similar(0.90).targetOffset(-86,21))  # check the result in the same time
    click(Pattern("prefab_trigger_range.png").similar(0.90)); type("1.5" + Key.ENTER)
    rightClick(Pattern("3dview_prefab_trigger_select_07.png").similar(0.90).targetOffset(-17,6))
    click(Pattern("prefab_trigger_range.png").similar(0.90)); type("1" + Key.ENTER)
    rightClick(Pattern("3dview_prefab_trigger_select_08.png").similar(0.90).targetOffset(0,28))
    click(Pattern("prefab_trigger_range.png").similar(0.90)); type("1.3" + Key.ENTER)
    find("3dview_prefab_loc_trigger_set_3.png")
except:
    configurator.save_screenshot(getBundlePath(), Screen())
    raise
finally:
    configurator.close_blender(p)