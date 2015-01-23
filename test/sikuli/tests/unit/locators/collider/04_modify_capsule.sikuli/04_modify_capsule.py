import configurator
p = configurator.start_it_up(getBundlePath(), "collider_capsule.blend")
try:
    wait("3dview_collider_capsule.png", 5)
    click("locator_centered_op.png"); find("3dview_collider_capsule_centered.png")
    click("collider_capsule_diameter.png"); type("1" + Key.ENTER); find("3dview_collider_capsule_diameter_1.png")
    click("collider_capsule_length.png"); type("3" + Key.ENTER); find("3dview_collider_capsule_length_3.png")
    click("locator_centered_op_pressed.png"); find("3dview_collider_capsule_decentered.png")
except:
    configurator.save_screenshot(getBundlePath(), Screen())
    raise
finally:
    configurator.close_blender(p)