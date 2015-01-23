import configurator, os
p = configurator.start_it_up(getBundlePath(), "prefab_locator_semaphore.blend")
try:
    mouseMove(Location(0,0)); wait("3dview_prefab_loc_semaphore.png", 5)
    click(Pattern("prefab_semaphore_id_none.png").similar(0.95).targetOffset(53,0))
    click(Pattern("prefab_semaphore_0_popup_pick.png").similar(0.80))
    click(Pattern("prefab_semaphore_profile.png").similar(0.95).targetOffset(53,0)); type("crossi")
    click(Pattern("prefab_semaphore_road_crossing-default_popup_pick.png").similar(0.90))
    click(Pattern("prefab_semaphore_type_use_profile.png").similar(0.90).targetOffset(54,1))
    click(Pattern("prefab_semaphore_model_only_popup_pick.png").similar(0.90))
    find(Pattern("prefab_semaphore_model_only_ui.png").similar(0.90))
    click(Pattern("prefab_semaphore_type_model_only.png").similar(0.90).targetOffset(55,1))
    click(Pattern("prefab_semaphore_barrier-manual_timed_popup_pick.png").similar(0.90))
    click(Pattern("prefab_semaphore_barrier-manual_timed_ui.png").targetOffset(-61,-11)); type("12" + Key.ENTER)  # Change Green light value
    click(Pattern("prefab_semaphore_barrier-manual_timed_ui.png").targetOffset(2,-11)); type("2.5" + Key.ENTER)  # Change Orange light value
    click(Pattern("prefab_semaphore_barrier-manual_timed_ui.png").targetOffset(62,-11)); type("22" + Key.ENTER)  # Change Red light value
    click(Pattern("prefab_semaphore_barrier-manual_timed_ui.png").targetOffset(126,-11)); type("1.5" + Key.ENTER)  # Change after-red Orange light value
    click(Pattern("prefab_semaphore_barrier-manual_timed_ui.png").targetOffset(0,11)); type("3" + Key.ENTER)  # Change Cycle Delay value
    hover(Location(400, 400))  # move cursor away from panels
    find(Pattern("prefab_semaphore_barrier-manual_timed_ui_altered.png").similar(0.95))
    click(Pattern("prefab_semaphore_type_barrier-manual_timed.png").similar(0.95).targetOffset(48,0))
    click(Pattern("prefab_semaphore_barrier-distance_activated_popup_pick.png").similar(0.90))
    click(Pattern("prefab_semaphore_barrier-distance_activated_ui.png").targetOffset(-37,-11)); type("160" + Key.ENTER)  # Change Green light value
    click(Pattern("prefab_semaphore_barrier-distance_activated_ui.png").targetOffset(37,-11)); type("200" + Key.ENTER)  # Change Orange light value
    click(Pattern("prefab_semaphore_barrier-distance_activated_ui.png").targetOffset(117,-11)); type("100" + Key.ENTER)  # Change Red light value
    click(Pattern("prefab_semaphore_barrier-distance_activated_ui.png").targetOffset(0,11)); type("2" + Key.ENTER)  # Change Cycle Delay value
    hover(Location(400, 400))  # move cursor away from panels
    find(Pattern("prefab_semaphore_barrier-distance_activated_ui_altered.png").similar(0.95))
except:
    configurator.save_screenshot(getBundlePath(), Screen())
    raise
finally:
    configurator.close_blender(p)