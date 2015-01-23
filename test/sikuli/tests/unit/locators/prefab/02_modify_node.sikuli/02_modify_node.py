import configurator, os
p = configurator.start_it_up(getBundlePath(), "prefab_locator_node.blend")
try:
    mouseMove(Location(0,0)); wait("3dview_model_loc-1.png", 5)
    #TODO: I guess this is not done test!
except:
    configurator.save_screenshot(getBundlePath(), Screen())
    raise
finally:
    configurator.close_blender(p)