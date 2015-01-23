def showAll():
    keyDown(Key.ALT); type("h"); keyUp(Key.ALT); type("a" + Key.ESC)

def confirmInput():
    type(Key.ENTER); type(Key.ESC)

import configurator, os
p = configurator.start_it_up(getBundlePath(), "default_3_variants.blend", delete_pix=False)
try:
    mouseMove(Location(0,0)); wait("3dview_variants_cubes_01.png", 5); hover("3dview_variants_cubes_01.png"); type(Key.ESC)
    doubleClick(Pattern("variant_list_add_14.png").similar(0.95).targetOffset(-77,-22))
    type("var" + Key.ENTER)
    find(Pattern("variant_list_add_16.png").similar(0.95))
    doubleClick(Pattern("variant_list_add_17.png").similar(0.95).targetOffset(-70,-2))
    type("var1" + Key.ENTER)
    find(Pattern("variant_list_add_18.png").similar(0.95))
    doubleClick(Pattern("variant_list_add_19.png").similar(0.95).targetOffset(-68,19))
    type("var2" + Key.ENTER)
    find(Pattern("variant_list_add_20.png").similar(0.95))
    hover(Location(450, 400))  # move cursor to the safe location
except:
    configurator.save_screenshot(getBundlePath(), Screen())
    raise
finally:
    configurator.close_blender(p)