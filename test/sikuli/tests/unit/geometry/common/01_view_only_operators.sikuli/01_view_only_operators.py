def showAll():
    keyDown(Key.ALT); type("h"); keyUp(Key.ALT); type("a" + Key.ESC); type(" ");

def confirmInput():
    type(Key.ENTER); type(Key.ESC)

import configurator, os
p = configurator.start_it_up(getBundlePath(), "all_objects.blend", delete_pix=False)
try:
    wait("3dview_all_objects.png", 5); hover("3dview_all_objects.png"); type(Key.ESC); type(" ");
    # MODEL OBJECTS
    type("Switch Visibility of Model Objects"); confirmInput(); find(Pattern("3dview_view_only_models.png").similar(0.96)); showAll()
    # SHADOW CASTERS
    type("Switch Visibility of Shadow Casters"); confirmInput(); find(Pattern("3dview_view_only_shadow_casters.png").similar(0.96)); showAll()
    # GLASS
    type("Switch Visibility of Glass Objects"); confirmInput(); find(Pattern("3dview_view_only_glass.png").similar(0.96));
except:
    configurator.save_screenshot(getBundlePath(), Screen())
    raise
finally:
    configurator.close_blender(p)