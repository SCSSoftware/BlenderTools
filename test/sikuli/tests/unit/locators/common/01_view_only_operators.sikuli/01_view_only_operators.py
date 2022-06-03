load("scs_bt_configurator.jar")

def showAll():
    keyDown(Key.ALT); type("h"); keyUp(Key.ALT); type("aa" + Key.ESC); type(Key.F3);

def confirmInput():
    type(Key.ENTER); type(Key.ESC)

import scs_bt_configurator
p = scs_bt_configurator.start_it_up(getBundlePath(), "all_objects.blend", delete_pix=False)
try:
    wait(Pattern("3dview_all_objects.png").exact(), 5); hover(Pattern("3dview_all_objects.png").exact()); type(Key.ESC); type(Key.F3);
    # PREFAB LOCATORS
    paste("View Prefab Navigation Locators"); confirmInput(); find(Pattern("3dview_view_only_prefab_nav.png").exact()); showAll()
    paste("View Prefab Spawn Locators"); confirmInput(); find(Pattern("3dview_view_only_prefab_spawn.png").exact()); showAll()
    paste("View Prefab Trigger Locators"); confirmInput(); find(Pattern("3dview_view_only_prefab_trigger-1.png").exact()); showAll()
    paste("View Prefab Map Locators"); confirmInput(); find(Pattern("3dview_view_only_prefab_map.png").exact()); showAll()
    paste("View Prefab Control Node Locators"); confirmInput(); find(Pattern("3dview_view_only_prefab_controle_node.png").exact()); showAll()
    paste("View Prefab Traffic Locators"); confirmInput(); find(Pattern("3dview_view_only_prefab_traffic.png").exact()); showAll()
    paste("View Prefab Sign Locators"); confirmInput(); find(Pattern("3dview_view_only_prefab_sign.png").exact()); showAll()
    paste("View Prefab Locators"); confirmInput(); find(Pattern("3dview_view_only_prefab.png").exact()); showAll()
    # COLLISION LOCATORS
    paste("View Collision Locators"); confirmInput(); find(Pattern("3dview_view_only_collision.png").exact()); showAll()
    # MODEL LOCATORS
    paste("View Model Locators"); confirmInput(); find(Pattern("3dview_view_only_model.png").exact()); showAll()
    # ALL LOCATORS
    paste("View All Locators"); confirmInput(); find(Pattern("3dview_view_only_locators.png").exact());
except:
    scs_bt_configurator.save_screenshot(getBundlePath(), Screen())
    raise
finally:
    scs_bt_configurator.close_blender(p)