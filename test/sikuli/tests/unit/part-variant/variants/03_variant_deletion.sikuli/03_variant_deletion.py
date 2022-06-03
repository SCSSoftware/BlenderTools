load("scs_bt_configurator.jar")
import scs_bt_configurator
p = scs_bt_configurator.start_it_up(getBundlePath(), "default_3_variants_named.blend", delete_pix=False)
try:
    mouseMove(Location(0,0)); wait(Pattern("3dview_variants_cubes_01.png").exact(), 5); hover(Pattern("3dview_variants_cubes_01.png").exact()); type(Key.ESC)
    click(Pattern("variant_list_add_10.png").exact().targetOffset(0,-11))
    click(Pattern("variant_list_deletion_01.png").exact().targetOffset(-58,-25))
    click(Pattern("variant_list_add_10.png").exact().targetOffset(0,-12))
    find(Pattern("variant_list_deletion_02.png").exact())
    find(Pattern("variant_list_deletion_03.png").exact())
    hover(Location(450, 400))  # move cursor to the safe location
except:
    scs_bt_configurator.save_screenshot(getBundlePath(), Screen())
    raise
finally:
    scs_bt_configurator.close_blender(p)