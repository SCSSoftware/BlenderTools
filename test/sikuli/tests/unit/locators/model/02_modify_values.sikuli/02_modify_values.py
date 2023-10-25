load("scs_bt_configurator.jar")
import scs_bt_configurator
p = scs_bt_configurator.start_it_up(getBundlePath(), "model_locator.blend")
try:
    mouseMove(Location(0,0)); wait(Pattern("3dview_init-1.png").exact(), 5)
    click(Pattern("model_name_empty.png").similar(0.95).targetOffset(14,1)); type("model_loc" + Key.ENTER); find(Pattern("3dview_model_name_changed.png").exact())
    click(Pattern("model_hookup_change.png").similar(0.95))
    paste("pedestrian_hookup mixer")
    click(Pattern("model_hookup_pedestrian_mixer_pick.png").exact())
    find(Pattern("model_hookup_pedestrian_mixer.png").similar(0.95))
except:
    scs_bt_configurator.save_screenshot(getBundlePath(), Screen())
    raise
finally:
    scs_bt_configurator.close_blender(p)