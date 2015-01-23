import configurator, os
p = configurator.start_it_up(getBundlePath(), "model_locator.blend")
try:
    mouseMove(Location(0,0)); wait(Pattern("3dview_init-1.png").similar(0.90), 5)
    click(Pattern("model_name_empty.png").similar(0.90).targetOffset(71,0)); type("model_loc" + Key.ENTER); find("3dview_model_name_changed.png")
    click(Pattern("model_hookup_change.png").similar(0.90).targetOffset(79,0)); type("show")
    click(Pattern("model_hookup_pick_showroom.png").similar(0.90)); find(Pattern("model_hookup_showroom.png").similar(0.90))
except:
    configurator.save_screenshot(getBundlePath(), Screen())
    raise
finally:
    configurator.close_blender(p)