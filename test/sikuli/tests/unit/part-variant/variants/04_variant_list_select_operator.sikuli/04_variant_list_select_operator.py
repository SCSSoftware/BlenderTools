def showAll():
    keyDown(Key.ALT); type("h"); keyUp(Key.ALT); type("a" + Key.ESC)

def confirmInput():
    type(Key.ENTER); type(Key.ESC)

import configurator, os
p = configurator.start_it_up(getBundlePath(), "default_3_variants_named.blend", delete_pix=False)
try:
    mouseMove(Location(0,0)); wait("3dview_variants_cubes_01.png", 5); hover("3dview_variants_cubes_01.png"); type(Key.ESC)
    click(Pattern("variant_list_select_and_view_01.png").similar(0.95).targetOffset(-29,-23))
    find(Pattern("variant_list_select_and_view_02.png").similar(0.95))
    click(Pattern("variant_list_select_and_view_01.png").similar(0.95).targetOffset(-29,-3))
    find(Pattern("variant_list_select_and_view_03.png").similar(0.95))
    click(Pattern("variant_list_select_and_view_01.png").similar(0.95).targetOffset(-29,17))
    find(Pattern("variant_list_select_and_view_04.png").similar(0.95))
    click(Pattern("variant_list_select_and_view_01.png").similar(0.95).targetOffset(-29,-23))
    find(Pattern("variant_list_select_and_view_05.png").similar(0.95))
    click(Pattern("variant_list_select_and_view_01.png").similar(0.95).targetOffset(-29,-3))
    find(Pattern("variant_list_select_and_view_03.png").similar(0.95))
    keyDown(Key.SHIFT); click(Pattern("variant_list_select_and_view_01.png").similar(0.95).targetOffset(-29,17)); keyUp(Key.SHIFT)
    find(Pattern("variant_list_select_and_view_06.png").similar(0.95))
    keyDown(Key.CTRL); click(Pattern("variant_list_select_and_view_01.png").similar(0.95).targetOffset(-29,17)); keyUp(Key.CTRL)
    find(Pattern("variant_list_select_and_view_07.png").similar(0.95))
    click(Pattern("variant_list_select_and_view_01.png").similar(0.95).targetOffset(-29,17))
    find(Pattern("variant_list_select_and_view_04.png").similar(0.95))
    hover(Location(450, 400))  # move cursor to the safe location
except:
    configurator.save_screenshot(getBundlePath(), Screen())
    raise
finally:
    configurator.close_blender(p)