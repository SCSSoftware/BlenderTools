def showAll():
    keyDown(Key.ALT); type("h"); keyUp(Key.ALT); type("a" + Key.ESC); type(" ");

def confirmInput():
    type(Key.ENTER); type(Key.ESC)

import configurator, os
p = configurator.start_it_up(getBundlePath(), "all_objects.blend", delete_pix=False)
try:
    wait("3dview_all_objects.png", 5); hover("3dview_all_objects.png"); type(Key.ESC); type(" ");
    # PREFAB LOCATORS
    type("Switch Visibility of Prefab Navigation Locators"); confirmInput(); find(Pattern("3dview_view_only_prefab_nav.png").similar(0.96)); showAll()
    type("Switch Visibility of Prefab Spawn Locators"); confirmInput(); find(Pattern("3dview_view_only_prefab_spawn.png").similar(0.96)); showAll()
    type("Switch Visibility of Prefab Trigger Locators"); confirmInput(); find(Pattern("3dview_view_only_prefab_trigger-1.png").similar(0.96)); showAll()
    type("Switch Visibility of Prefab Map Locators"); confirmInput(); find(Pattern("3dview_view_only_prefab_map.png").similar(0.96)); showAll()
    type("Switch Visibility of Prefab Control Node Locators"); confirmInput(); find(Pattern("3dview_view_only_prefab_controle_node.png").similar(0.96)); showAll()
    type("Switch Visibility of Prefab Traffic Locators"); confirmInput(); find(Pattern("3dview_view_only_prefab_traffic.png").similar(0.96)); showAll()
    type("Switch Visibility of Prefab Sign Locators"); confirmInput(); find(Pattern("3dview_view_only_prefab_sign.png").similar(0.96)); showAll()
    type("Switch Visibility of Prefab Locators"); confirmInput(); find(Pattern("3dview_view_only_prefab.png").similar(0.96)); showAll()
    # COLLISION LOCATORS
    type("Switch Visibility of Collision Locators"); confirmInput(); find(Pattern("3dview_view_only_collision.png").similar(0.96)); showAll()
    # MODEL LOCATORS
    type("Switch Visibility of Model Locators"); confirmInput(); find(Pattern("3dview_view_only_model.png").similar(0.96)); showAll()
    # ALL LOCATORS
    type("Switch Visibility of All Locators"); confirmInput(); find(Pattern("3dview_view_only_locators.png").similar(0.96));
except:
    configurator.save_screenshot(getBundlePath(), Screen())
    raise
finally:
    configurator.close_blender(p)