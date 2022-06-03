def showAll():
    keyDown(Key.ALT); type("h"); keyUp(Key.ALT); type("aa" + Key.ESC)

def confirmInput():
    type(Key.ENTER); type(Key.ESC)

load("scs_bt_configurator.jar")
import scs_bt_configurator
p = scs_bt_configurator.start_it_up(getBundlePath(), "all_objects.blend", delete_pix=False)
try:
    wait(Pattern("3dview_all.png").similar(0.96), 5); hover(Pattern("3dview_all.png").similar(0.96)); showAll()
    # MODEL OBJECTS
    type(Key.F3 + "Select Model Objects"); confirmInput(); find(Pattern("3dview_select_models.png").similar(0.96)); showAll(); wait(Pattern("3dview_all.png").similar(0.96), 2)
    # SHADOW CASTERS
    type(Key.F3 + "Select Shadow Casters"); confirmInput(); find(Pattern("3dview_select_shadow_casters.png").similar(0.96)); showAll(); wait(Pattern("3dview_all.png").similar(0.96), 2)
    # GLASS OBJECTS
    type(Key.F3 + "Select Glass Objects"); confirmInput(); find(Pattern("3dview_select_glass.png").similar(0.96)); showAll(); wait(Pattern("3dview_all.png").similar(0.96), 2)
except:
    scs_bt_configurator.save_screenshot(getBundlePath(), Screen())
    raise
finally:
    scs_bt_configurator.close_blender(p)