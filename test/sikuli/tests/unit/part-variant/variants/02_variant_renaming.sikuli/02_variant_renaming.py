load("scs_bt_configurator.jar")
import scs_bt_configurator
p = scs_bt_configurator.start_it_up(getBundlePath(), "default_3_variants.blend", delete_pix=False)
try:
    mouseMove(Location(0,0)); wait(Pattern("3dview_variants_cubes_01.png").exact(), 5); hover(Pattern("3dview_variants_cubes_01.png").exact()); type(Key.ESC)
    doubleClick(Pattern("variant_list_add_14.png").exact().targetOffset(-60,-26))
    type("var" + Key.ENTER)
    find(Pattern("variant_list_add_16.png").exact())
    doubleClick(Pattern("variant_list_add_17.png").exact().targetOffset(-53,-4))
    type("var1" + Key.ENTER)
    find(Pattern("variant_list_add_18.png").exact())
    doubleClick(Pattern("variant_list_add_19.png").exact().targetOffset(-56,15))
    type("var2" + Key.ENTER)
    find(Pattern("variant_list_add_20.png").exact())
    hover(Location(450, 400))  # move cursor to the safe location
except:
    scs_bt_configurator.save_screenshot(getBundlePath(), Screen())
    raise
finally:
    scs_bt_configurator.close_blender(p)