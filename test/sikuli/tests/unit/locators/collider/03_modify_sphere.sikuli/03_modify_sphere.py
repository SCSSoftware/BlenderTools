load("scs_bt_configurator.jar")
import scs_bt_configurator
p = scs_bt_configurator.start_it_up(getBundlePath(), "collider_sphere.blend")
try:
    wait(Pattern("3dview_collider_sphere.png").exact(), 5)
    click("locator_centered_op.png"); find(Pattern("3dview_collider_sphere_centered.png").exact())
    click("collider_sphere_diameter.png"); type("1" + Key.ENTER); find(Pattern("3dview_collider_sphere_diameter_1.png").exact())
    click("locator_centered_op_pressed.png"); find(Pattern("3dview_collider_sphere_decentered.png").exact())
except:
    scs_bt_configurator.save_screenshot(getBundlePath(), Screen())
    raise
finally:
    scs_bt_configurator.close_blender(p)