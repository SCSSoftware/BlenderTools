import configurator, os
p = configurator.start_it_up(getBundlePath(), "collider_box.blend")
try:
    wait("3dview_locator_collision.png", 5)
    click("box_z_size_1.png"); type("2" + Key.ENTER); find("box_resized_z_2.png")
    click("locator_centered_op.png"); find("box_centered.png")
    click("locator_centered_op_pressed.png"); find("box_resized_z_2.png")
    click("box_y_size_1.png"); type("0.5" + Key.ENTER); find("box_resized_y_0_5.png")
except:
    configurator.save_screenshot(getBundlePath(), Screen())
    raise
finally:
    configurator.close_blender(p)