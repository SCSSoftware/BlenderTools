load("scs_bt_configurator.jar")
import scs_bt_configurator
p = scs_bt_configurator.start_it_up(getBundlePath(), "default_3_variants_named.blend", delete_pix=False)
try:
    mouseMove(Location(0,0)); wait(Pattern("3dview_variants_cubes_01.png").exact(), 5); hover(Pattern("3dview_variants_cubes_01.png").exact()); type(Key.ESC)
    click(Pattern("variant_list_select_and_view_01.png").exact().targetOffset(-27,-24))
    find(Pattern("variant_list_select_and_view_02.png").exact())
    click(Pattern("variant_list_select_and_view_01.png").exact().targetOffset(-25,-3))
    find(Pattern("variant_list_select_and_view_03.png").exact())
    click(Pattern("variant_list_select_and_view_01.png").exact().targetOffset(-26,13))
    find(Pattern("variant_list_select_and_view_04.png").exact())
    click(Pattern("variant_list_select_and_view_01.png").exact().targetOffset(-27,-25))
    find(Pattern("variant_list_select_and_view_05.png").exact())
    click(Pattern("variant_list_select_and_view_01.png").exact().targetOffset(-26,-3))
    find(Pattern("variant_list_select_and_view_03.png").exact())
    keyDown(Key.SHIFT); click(Pattern("variant_list_select_and_view_01.png").exact().targetOffset(-26,15)); keyUp(Key.SHIFT)
    find(Pattern("variant_list_select_and_view_06.png").exact())
    keyDown(Key.CTRL); click(Pattern("variant_list_select_and_view_01.png").exact().targetOffset(-24,15)); keyUp(Key.CTRL)
    find(Pattern("variant_list_select_and_view_07.png").exact())
    click(Pattern("variant_list_select_and_view_01.png").exact().targetOffset(-25,15))
    find(Pattern("variant_list_select_and_view_04.png").exact())
    hover(Location(450, 400))  # move cursor to the safe location
except:
    scs_bt_configurator.save_screenshot(getBundlePath(), Screen())
    raise
finally:
    scs_bt_configurator.close_blender(p)