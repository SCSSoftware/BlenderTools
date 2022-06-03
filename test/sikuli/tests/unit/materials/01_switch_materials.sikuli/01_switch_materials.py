load("scs_bt_configurator.jar")
import scs_bt_configurator
p = scs_bt_configurator.start_it_up(getBundlePath(), "startup.blend", delete_pix=False)
try:
    wait(Pattern("3dview_init.png").exact(), 5); hover(Pattern("3dview_init.png").exact()); type(Key.ESC)

    # Purpose of the test is checking if everything works as expected
    # when duplicating material and then switching between them on object parented to scs root with looks (QA: 174475)

    click(Pattern("material_selection.png").exact().targetOffset(75,-1))
    click(Pattern("material001_selection.png").exact().targetOffset(-91,2))
    click(Pattern("material001_selection_popup.png").exact().targetOffset(-1,-10))
    wait(0.1)
    find(Pattern("3dview_init.png").exact())
except:
    scs_bt_configurator.save_screenshot(getBundlePath(), Screen())
    raise
finally:
    scs_bt_configurator.close_blender(p)