import configurator
p = configurator.start_it_up(getBundlePath(), "collider_sphere.blend")
try:
    wait("3dview_collider_sphere-1.png", 5)
    click("locator_centered_op.png"); find("3dview_collider_sphere_centered.png")
    click("collider_sphere_diameter.png"); type("1" + Key.ENTER); find("3dview_collider_sphere_diameter_1.png")
    click("locator_centered_op_pressed.png"); find("3dview_collider_sphere_decentered.png")
except:
    configurator.save_screenshot(getBundlePath(), Screen())
    raise
finally:
    configurator.close_blender(p)