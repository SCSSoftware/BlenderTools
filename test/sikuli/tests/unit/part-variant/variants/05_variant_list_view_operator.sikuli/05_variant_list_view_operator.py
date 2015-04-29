def showAll():
    keyDown(Key.ALT); type("h"); keyUp(Key.ALT); type("a" + Key.ESC)

def confirmInput():
    type(Key.ENTER); type(Key.ESC)

import configurator, os
p = configurator.start_it_up(getBundlePath(), "default_3_variants_named.blend", delete_pix=False)
try:
    mouseMove(Location(0,0)); wait("3dview_variants_cubes_01.png", 5); hover("3dview_variants_cubes_01.png"); type(Key.ESC)
    click(Pattern("variant_list_select_and_view_01.png").similar(0.95).targetOffset(-11,-23))
    find(Pattern("variant_list_select_and_view_08.png").similar(0.90))
    click(Pattern("variant_list_select_and_view_01.png").similar(0.95).targetOffset(-11,-4))
    find(Pattern("variant_list_select_and_view_09.png").similar(0.84))
    click(Pattern("variant_list_select_and_view_01.png").similar(0.95).targetOffset(-11,16))
    find(Pattern("variant_list_select_and_view_10.png").similar(0.90))
    hover(Location(450, 400))  # move cursor to the safe location
except:
    configurator.save_screenshot(getBundlePath(), Screen())
    raise
finally:
    configurator.close_blender(p)