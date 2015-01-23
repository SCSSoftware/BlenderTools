def showAll():
    keyDown(Key.ALT); type("h"); keyUp(Key.ALT); type("a" + Key.ESC)

def confirmInput():
    type(Key.ENTER); type(Key.ESC)

import configurator, os
p = configurator.start_it_up(getBundlePath(), "scs_game_cubes.blend", delete_pix=False)
try:
    mouseMove(Location(0,0)); wait("3dview_variants_cubes_01.png", 5); hover("3dview_variants_cubes_01.png"); type(Key.ESC)
    click(Pattern("variant_list_add_10.png").exact().targetOffset(0,-10))
    find(Pattern("variant_list_add_11.png").similar(0.95))
    click(Pattern("variant_list_add_03.png").similar(0.95))
    click(Pattern("variant_list_add_04.png").similar(0.95).targetOffset(0,20))
    find(Pattern("variant_list_add_05.png").similar(0.95))
    click(Pattern("variant_list_add_10.png").exact().targetOffset(0,-10))
    find(Pattern("variant_list_add_12.png").similar(0.95))
    click(Pattern("variant_list_add_13.png").similar(0.90).targetOffset(0,-5))
    click(Pattern("variant_list_add_10.png").exact().targetOffset(0,-10))
    find(Pattern("variant_list_add_14.png").similar(0.95))
    click(Pattern("variant_list_add_15.png").similar(0.95).targetOffset(0,12))
    hover(Location(450, 400))  # move cursor to the safe location
except:
    configurator.save_screenshot(getBundlePath(), Screen())
    raise
finally:
    configurator.close_blender(p)
