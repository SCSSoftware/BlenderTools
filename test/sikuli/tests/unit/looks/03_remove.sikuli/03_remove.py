load("scs_bt_configurator.jar")
import scs_bt_configurator
p = scs_bt_configurator.start_it_up(getBundlePath(), "looks.blend")
try:
    wait(Pattern("startup.png").similar(0.98),5)
    click(Pattern("add_remove_buttons.png").exact().targetOffset(108,9)); find(Pattern("green_view.png").similar(0.98))
except:
    scs_bt_configurator.save_screenshot(getBundlePath(), Screen())
    raise
finally:
    scs_bt_configurator.close_blender(p)