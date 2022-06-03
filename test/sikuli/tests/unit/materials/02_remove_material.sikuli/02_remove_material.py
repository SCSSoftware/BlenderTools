load("scs_bt_configurator.jar")
import scs_bt_configurator
p = scs_bt_configurator.start_it_up(getBundlePath(), "startup.blend", delete_pix=False)
try:
    wait(Pattern("3dview_init.png").exact(), 5); hover(Pattern("3dview_init.png").exact()); type(Key.ESC)

    # Purpose of the test is checking if everything works as expected
    # while removing material from object and consequentially from looks in scs root (QA: 174475)

    click(Pattern("material_selection.png").exact().targetOffset(96,-1))
    find(Pattern("3dview_init.png").exact())
except:
    scs_bt_configurator.save_screenshot(getBundlePath(), Screen())
    raise
finally:
    scs_bt_configurator.close_blender(p)