load("scs_bt_configurator.jar")

def showAll():
    keyDown(Key.ALT); type("h"); keyUp(Key.ALT); type("aa" + Key.ESC); type(Key.F3);

def confirmInput():
    type(Key.ENTER); type(Key.ESC)

import scs_bt_configurator
p = scs_bt_configurator.start_it_up(getBundlePath(), "all_objects.blend", delete_pix=False)
try:
    mouseMove(Location(0,0)); wait(Pattern("3dview_all.png").exact(), 5); hover(Pattern("3dview_all.png").exact()); type(Key.ESC); type(Key.F3);
    # PREFAB LOCATORS
    paste("Select Prefab Navigation Locators"); confirmInput(); find(Pattern("3dview_select_prefab_nav.png").exact()); showAll()
    paste("Select Prefab Spawn Locators"); confirmInput(); find(Pattern("3dview_select_prefab_spawn.png").exact()); showAll()
    paste("Select Prefab Trigger Locators"); confirmInput(); find(Pattern("3dview_select_prefab_trigger.png").similar(0.96)); showAll()
    paste("Select Prefab Map Locators"); confirmInput(); find(Pattern("3dview_select_prefab_map.png").exact()); showAll()
    paste("Select Prefab Control Node Locators"); confirmInput(); find(Pattern("3dview_select_prefab_controle_node.png").exact()); showAll()
    paste("Select Prefab Traffic Locators"); confirmInput(); find(Pattern("3dview_select_prefab_traffic.png").exact()); showAll()
    paste("Select Prefab Sign Locators"); confirmInput(); find(Pattern("3dview_select_prefab_sign.png").exact()); showAll()
    paste("Select Prefab Locators"); confirmInput(); find(Pattern("3dview_select_prefab.png").exact()); showAll()
    # COLLISION LOCATORS
    paste("Select Collision Locators"); confirmInput(); find(Pattern("3dview_select_collision.png").exact()); showAll()
    # MODEL LOCATORS
    paste("Select Model Locators"); confirmInput(); find(Pattern("3dview_select_model.png").exact()); showAll()
    # ALL LOCATORS
    paste("Select All Locators"); confirmInput(); find(Pattern("3dview_select_locators.png").exact())
except:
    scs_bt_configurator.save_screenshot(getBundlePath(), Screen())
    raise
finally:
    scs_bt_configurator.close_blender(p)