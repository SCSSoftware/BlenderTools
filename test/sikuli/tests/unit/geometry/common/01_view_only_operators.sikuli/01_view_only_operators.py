def showAll():
    hover(Location(600, 300)); keyDown(Key.ALT); type("h"); keyUp(Key.ALT); type("aa" + Key.ESC)

load("scs_bt_configurator.jar")
import scs_bt_configurator
p = scs_bt_configurator.start_it_up(getBundlePath(), "all_objects.blend", delete_pix=False)
try:
    wait(Pattern("3dview_all_objects.png").exact(), 5)
    visibility_tools_region = find(Pattern("visibility_tools.png").exact())
    # MODEL OBJECTS
    visibility_tools_region.click(Pattern("view_only_models.png").exact()); wait(Pattern("3dview_view_only_models.png").similar(0.96), 1); showAll(); wait(Pattern("3dview_all_objects.png").similar(0.96), 2)
    # SHADOW CASTERS
    visibility_tools_region.click(Pattern("view_only_shadow_casters.png").exact()); wait(Pattern("3dview_view_only_shadow_casters.png").similar(0.96), 1); showAll(); wait(Pattern("3dview_all_objects.png").similar(0.96), 2)
    # GLASS
    visibility_tools_region.click(Pattern("view_only_glass.png").exact()); wait(Pattern("3dview_view_only_glass.png").similar(0.96), 1); showAll(); wait(Pattern("3dview_all_objects.png").similar(0.96), 2)
except:
    scs_bt_configurator.save_screenshot(getBundlePath(), Screen())
    raise
finally:
    scs_bt_configurator.close_blender(p)