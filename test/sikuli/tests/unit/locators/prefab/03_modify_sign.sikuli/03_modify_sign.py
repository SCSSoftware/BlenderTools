import configurator, os
p = configurator.start_it_up(getBundlePath(), "prefab_locator_sign.blend")
try:
    mouseMove(Location(0,0)); wait("3dview_prefab_loc_sign.png", 5)
    hover(Location(450, 400))
    type("g")
    type(".2"); type(Key.TAB)
    type("1"); type(Key.TAB)
    type("1"); type(Key.ENTER)
    click("add_root.png")
    rightClick("3dview_prefab_sign_select.png")
    click(Pattern("prefab_sign_sign_model.png").similar(0.95).targetOffset(37,0)); type("roadsign")
    click(Pattern("prefab_uk-al_roadsign_popup_pick.png").similar(0.90))
    click(Pattern("panel_expand_parts.png").similar(0.95))
    find(Pattern("panel_parts_list.png").similar(0.95))
except:
    configurator.save_screenshot(getBundlePath(), Screen())
    raise
finally:
    configurator.close_blender(p)