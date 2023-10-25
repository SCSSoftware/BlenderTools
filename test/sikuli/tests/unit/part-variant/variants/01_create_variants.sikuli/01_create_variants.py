load("scs_bt_configurator.jar")
import scs_bt_configurator
p = scs_bt_configurator.start_it_up(getBundlePath(), "scs_game_cubes.blend", delete_pix=False)
try:
    mouseMove(Location(0,0)); wait(Pattern("3dview_variants_cubes_01.png").exact(), 5); hover(Pattern("3dview_variants_cubes_01.png").exact()); type(Key.ESC)
    click(Pattern("variant_list_add_10.png").exact().targetOffset(0,-30))
    find(Pattern("variant_list_add_11.png").similar(0.95))
    click(Pattern("variant_list_add_03.png").similar(0.89).targetOffset(0,20))
    mouseMove(-100, 0); click(Pattern("variant_list_add_04.png").similar(0.92))
    mouseMove(-100, 0); find(Pattern("variant_list_add_05.png").similar(0.92))
    click(Pattern("variant_list_add_10.png").exact().targetOffset(0,-29))
    find(Pattern("variant_list_add_12.png").similar(0.92))
    click(Pattern("variant_list_add_13.png").similar(0.97).targetOffset(0,-5))
    click(Pattern("variant_list_add_10.png").exact().targetOffset(0,-30))
    find(Pattern("variant_list_add_14.png").similar(0.91))
    click(Pattern("variant_list_add_15.png").exact().targetOffset(0,12))
    hover(Location(450, 400))  # move cursor to the safe location
    find(Pattern("variant_list_final.png").exact())
except:
    scs_bt_configurator.save_screenshot(getBundlePath(), Screen())
    raise
finally:
    scs_bt_configurator.close_blender(p)
