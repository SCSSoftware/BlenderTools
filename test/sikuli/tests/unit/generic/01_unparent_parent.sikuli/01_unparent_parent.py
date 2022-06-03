load("scs_bt_configurator.jar")
import scs_bt_configurator
p = scs_bt_configurator.start_it_up(getBundlePath(), "startup.blend", delete_pix=False)
try:
    wait(Pattern("3dview_init.png").exact(), 5); hover(Pattern("3dview_init.png").exact()); type(Key.ESC)

    # Purpose of the test is checking if everything works as expected
    # on parent clearing and then reparent it (QA: 174475)

    keyDown(Key.ALT); type("p"); keyUp(Key.ALT); type(Key.ENTER + Key.ENTER)  # clear parent
    keyDown(Key.SHIFT); click(Pattern("3dview_init.png").exact().targetOffset(-14,-157)); keyUp(Key.SHIFT)
    keyDown(Key.CTRL); type("p"); keyUp(Key.CTRL); type(Key.ENTER)  # re-parent
    find(Pattern("3dview_reparented.png").exact())
except:
    scs_bt_configurator.save_screenshot(getBundlePath(), Screen())
    raise
finally:
    scs_bt_configurator.close_blender(p)