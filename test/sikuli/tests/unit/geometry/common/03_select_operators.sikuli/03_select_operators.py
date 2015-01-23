def showAll():
    keyDown(Key.ALT); type("h"); keyUp(Key.ALT); type("a" + Key.ESC); type(" ");

def confirmInput():
    type(Key.ENTER); type(Key.ESC)

import configurator, os
p = configurator.start_it_up(getBundlePath(), "all_objects.blend", delete_pix=False)
try:
    wait(Pattern("3dview_all.png").similar(0.96), 5); hover(Pattern("3dview_all.png").similar(0.96)); type(Key.ESC); type(" ");
    # MODEL OBJECTS
    type("Select Model Objects"); confirmInput(); find(Pattern("3dview_select_models.png").similar(0.96)); showAll()
    # SHADOW CASTERS
    type("Select Shadow Casters"); confirmInput(); find(Pattern("3dview_select_shadow_casters.png").similar(0.96)); showAll()
    # GLASS OBJECTS
    type("Select Glass Objects"); confirmInput(); find(Pattern("3dview_select_glass.png").similar(0.96))
except:
    configurator.save_screenshot(getBundlePath(), Screen())
    raise
finally:
    configurator.close_blender(p)