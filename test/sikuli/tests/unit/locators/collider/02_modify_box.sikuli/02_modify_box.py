load("scs_bt_configurator.jar")
import scs_bt_configurator
p = scs_bt_configurator.start_it_up(getBundlePath(), "collider_box.blend")
try:
    wait(Pattern("3dview_locator_collision.png").exact(), 5)
    click("box_z_size_1.png"); type("2" + Key.ENTER); find(Pattern("box_resized_z_2.png").exact())
    click("locator_centered_op.png"); find(Pattern("box_centered.png").exact())
    click("locator_centered_op_pressed.png"); find(Pattern("box_resized_z_2.png").exact())
    click("box_y_size_1.png"); type("0.5" + Key.ENTER); find(Pattern("box_resized_y_0_5.png").exact())
except:
    scs_bt_configurator.save_screenshot(getBundlePath(), Screen())
    raise
finally:
    scs_bt_configurator.close_blender(p)