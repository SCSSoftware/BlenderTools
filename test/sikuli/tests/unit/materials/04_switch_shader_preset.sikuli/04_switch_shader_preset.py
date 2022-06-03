load("scs_bt_configurator.jar")
import scs_bt_configurator
p = scs_bt_configurator.start_it_up(getBundlePath(), "startup.blend", delete_pix=False)
try:
    wait(Pattern("3dview_init.png").exact(), 5); hover(Pattern("3dview_init.png").exact()); type(Key.ESC)

    # Purpose of the test is checking if everything works as expected
    # when switching shader preset on object whos material is part of the scs look (QA: 174475)

    click(Pattern("shader_preset_original.png").exact().targetOffset(51,1))
    click(Pattern("shader_preset_popup_select.png").exact())
    find(Pattern("material_effect_dif_spec.png").exact())
    find(Pattern("3dview_init.png").exact())
except:
    scs_bt_configurator.save_screenshot(getBundlePath(), Screen())
    raise
finally:
    scs_bt_configurator.close_blender(p)