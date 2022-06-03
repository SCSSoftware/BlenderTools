load("scs_bt_configurator.jar")
import scs_bt_configurator
p = scs_bt_configurator.start_it_up(getBundlePath(), "prefab_locator_node.blend")
try:
    mouseMove(Location(0,0)); wait(Pattern("3dview_scene_init.png").exact(), 5)
    find(Pattern("control_node_panel.png").exact())  # since nothing cna be visually changed just check if panel is present
except:
    scs_bt_configurator.save_screenshot(getBundlePath(), Screen())
    raise
finally:
    scs_bt_configurator.close_blender(p)