def showAll():
    keyDown(Key.ALT); type("h"); keyUp(Key.ALT); type("a" + Key.ESC); type(" ");

def confirmInput():
    type(Key.ENTER); type(Key.ESC)

import configurator, os
p = configurator.start_it_up(getBundlePath(), "all_objects.blend", delete_pix=False)
try:
    mouseMove(Location(0,0)); wait(Pattern("3dview_all.png").similar(0.98), 5); hover(Pattern("3dview_all.png").similar(0.98)); type(Key.ESC); type(" ");
    # PREFAB LOCATORS 
    type("Select Prefab Navigation Locators"); confirmInput(); find(Pattern("3dview_select_prefab_nav.png").similar(0.98)); showAll()
    type("Select Prefab Spawn Locators"); confirmInput(); find(Pattern("3dview_select_prefab_spawn.png").similar(0.98)); showAll()
    type("Select Prefab Trigger Locators"); confirmInput(); find(Pattern("3dview_select_prefab_trigger.png").similar(0.96)); showAll()
    type("Select Prefab Map Locators"); confirmInput(); find(Pattern("3dview_select_prefab_map.png").similar(0.98)); showAll()
    type("Select Prefab Control Node Locators"); confirmInput(); find(Pattern("3dview_select_prefab_controle_node.png").similar(0.98)); showAll()
    type("Select Prefab Traffic Locators"); confirmInput(); find(Pattern("3dview_select_prefab_traffic.png").similar(0.98)); showAll()
    type("Select Prefab Sign Locators"); confirmInput(); find(Pattern("3dview_select_prefab_sign.png").similar(0.98)); showAll()
    type("Select Prefab Locators"); confirmInput(); find(Pattern("3dview_select_prefab.png").similar(0.98)); showAll()
    # COLLISION LOCATORS
    type("Select Collision Locators"); confirmInput(); find(Pattern("3dview_select_collision.png").similar(0.98)); showAll()
    # MODEL LOCATORS
    type("Select Model Locators"); confirmInput(); find(Pattern("3dview_select_model.png").similar(0.98)); showAll()
    # ALL LOCATORS
    type("Select All Locators"); confirmInput(); find(Pattern("3dview_select_locators.png").similar(0.98))
except:
    configurator.save_screenshot(getBundlePath(), Screen())
    raise
finally:
    configurator.close_blender(p)