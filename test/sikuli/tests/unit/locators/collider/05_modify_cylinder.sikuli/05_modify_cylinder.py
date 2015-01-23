import configurator
p = configurator.start_it_up(getBundlePath(), "collider_cylinder.blend")
try:
    wait("3dview_collider_cylinder.png", 5)
    click("locator_centered_op.png"); find("3dview_collider_cylinder_centered.png")
    click("collider_cylinder_diameter.png"); type("1" + Key.ENTER); find("3dview_collider_cylinder_diameter_1.png")
    click("collider_cylinder_length.png"); type("3" + Key.ENTER); find("3dview_collider_cylinder_length_3.png")
    click("locator_centered_op_pressed.png"); find("3dview_collider_cylinder_decentered.png")
except:
    configurator.save_screenshot(getBundlePath(), Screen())
    raise
finally:
    configurator.close_blender(p)