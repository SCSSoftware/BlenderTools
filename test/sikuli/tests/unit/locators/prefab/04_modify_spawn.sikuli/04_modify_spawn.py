import configurator, os
p = configurator.start_it_up(getBundlePath(), "prefab_locator_spawn.blend")
try:
    mouseMove(Location(0,0)); wait("3dview_prefab_loc_spawn.png", 5)
    click(Pattern("prefab_spawn_spawn_type_none.png").similar(0.90).targetOffset(35,0))
    click(Pattern("prefab_spawn_trailer_popup_pick.png").similar(0.95))
except:
    configurator.save_screenshot(getBundlePath(), Screen())
    raise
finally:
    configurator.close_blender(p)