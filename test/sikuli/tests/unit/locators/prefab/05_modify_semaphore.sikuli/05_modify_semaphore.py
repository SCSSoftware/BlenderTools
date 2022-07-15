load("scs_bt_configurator.jar")
import scs_bt_configurator
p = scs_bt_configurator.start_it_up(getBundlePath(), "prefab_locator_semaphore.blend")
try:
    mouseMove(Location(0,0)); wait(Pattern("3dview_initial_scene.png").exact(), 5)
    click(Pattern("prefab_semaphore_id_none.png").targetOffset(53,0))
    click(Pattern("prefab_semaphore_0_popup_pick.png").similar(0.80))
    click(Pattern("prefab_semaphore_profile.png").targetOffset(53,0)); type("crossi")
    click(Pattern("prefab_semaphore_road_crossing-default_popup_pick.png").similar(0.90))
    click(Pattern("prefab_semaphore_type_use_profile.png").targetOffset(54,1))
    click(Pattern("prefab_semaphore_model_only_popup_pick.png").similar(0.90))
    find(Pattern("prefab_semaphore_model_only_ui.png").similar(0.90))
    click(Pattern("prefab_semaphore_type_model_only.png").targetOffset(55,1))
    click(Pattern("prefab_semaphore_barrier-manual_timed_popup_pick.png").similar(0.90))
    click(Pattern("prefab_semaphore_barrier-manual_timed_ui.png").targetOffset(-111,-12)); type("12" + Key.ENTER)  # Change Green light value
    click(Pattern("prefab_semaphore_barrier-manual_timed_ui.png").targetOffset(-34,-13)); type("2.5" + Key.ENTER)  # Change Orange light value
    click(Pattern("prefab_semaphore_barrier-manual_timed_ui.png").targetOffset(44,-14)); type("22" + Key.ENTER)  # Change Red light value
    click(Pattern("prefab_semaphore_barrier-manual_timed_ui.png").targetOffset(126,-11)); type("1.5" + Key.ENTER)  # Change after-red Orange light value
    click(Pattern("prefab_semaphore_barrier-manual_timed_ui.png").targetOffset(0,11)); type("3" + Key.ENTER)  # Change Cycle Delay value
    hover(Location(400, 400))  # move cursor away from panels
    find(Pattern("prefab_semaphore_barrier-manual_timed_ui_altered.png").exact())
    click(Pattern("prefab_semaphore_type_barrier-manual_timed.png").targetOffset(48,0))
    click(Pattern("prefab_semaphore_barrier-distance_activated_popup_pick.png").similar(0.90))
    click(Pattern("prefab_semaphore_barrier-distance_activated_ui.png").targetOffset(-114,-11)); type("100" + Key.ENTER)  # Change Green light value
    click(Pattern("prefab_semaphore_barrier-distance_activated_ui.png").targetOffset(-31,-14)); type("500" + Key.ENTER)  # Change Orange light value
    click(Pattern("prefab_semaphore_barrier-distance_activated_ui.png").targetOffset(41,-14)); type("300" + Key.ENTER)  # Change Red light value
    click(Pattern("prefab_semaphore_barrier-distance_activated_ui.png").targetOffset(126,-11)); type("50" + Key.ENTER)  # Change after-red Orange light value    
    click(Pattern("prefab_semaphore_barrier-distance_activated_ui.png").targetOffset(0,11)); type("6" + Key.ENTER)  # Change Cycle Delay value
    hover(Location(400, 400))  # move cursor away from panels
    find(Pattern("prefab_semaphore_barrier-distance_activated_ui_altered.png").exact())
except:
    scs_bt_configurator.save_screenshot(getBundlePath(), Screen())
    raise
finally:
    scs_bt_configurator.close_blender(p)