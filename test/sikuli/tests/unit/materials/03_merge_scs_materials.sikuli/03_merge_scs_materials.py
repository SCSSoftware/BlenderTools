load("scs_bt_configurator.jar")
import scs_bt_configurator
p = scs_bt_configurator.start_it_up(getBundlePath(), "startup.blend", delete_pix=False)
try:
    wait(Pattern("3dview_init.png").exact(), 5); hover(Pattern("3dview_init.png").exact()); type(Key.ESC)

    # Purpose of the test is checking if everything works as expected
    # when Merge SCS Materials operator is used on materials that are also part of some scs look (QA: 174475)

    find(Pattern("material_slots_01.png").exact())
    type(Key.F3 + "merge scs materials" + Key.ENTER)
    click(Pattern("material_merge_popup.png").exact().targetOffset(-3,74))
    find(Pattern("material_slots_02.png").exact())
except:
    scs_bt_configurator.save_screenshot(getBundlePath(), Screen())
    raise
finally:
    scs_bt_configurator.close_blender(p)