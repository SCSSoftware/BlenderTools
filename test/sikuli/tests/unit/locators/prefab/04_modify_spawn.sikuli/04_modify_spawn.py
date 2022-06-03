load("scs_bt_configurator.jar")
import scs_bt_configurator
p = scs_bt_configurator.start_it_up(getBundlePath(), "prefab_locator_spawn.blend")
try:
    mouseMove(Location(0,0)); wait(Pattern("3dview_scene_init.png").exact(), 5)
    click(Pattern("spawn_type_prop.png").exact())
    click(Pattern("trailer_spaw_type_selection.png").exact())
    find(Pattern("spawn_type_prop_trailer.png").exact())
except:
    scs_bt_configurator.save_screenshot(getBundlePath(), Screen())
    raise
finally:
    scs_bt_configurator.close_blender(p)