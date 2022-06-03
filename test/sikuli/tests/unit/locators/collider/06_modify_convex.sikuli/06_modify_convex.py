load("scs_bt_configurator.jar")
import scs_bt_configurator
p = scs_bt_configurator.start_it_up(getBundlePath(), "collider_convex.blend")
try:
    wait(Pattern("3dview_collider_convex.png").exact(), 5)
    click("collider_convex_make_convex.png"); find(Pattern("3dview_collider_convex_created-1.png").exact())
    click("collider_convex_convert_to_loc.png")
    click("collider_convex_mesh_to_convex_op_header.png"); click("collider_convex_delete_original_geo.png");  click("collider_convex_mesh_to_convex_op_header.png"); find(Pattern("3dview_collider_convex_loc_created.png").exact())
    click(Pattern("collider_convex_faces.png").similar(0.90)); hover(Pattern("3dview_collider_convex_faces_off-1.png").exact())
    type(Key.ESC + "z" + "4") # esc used to get focus for sure and the switch to wireframe
    click("collider_convex_collision_margin.png"); type(".5" + Key.ENTER); hover(Pattern("3dview_collider_convex_margin_05-1.png").exact())
    type(Key.ESC + "x" + Key.ENTER); click()  # delete collision locator
    keyDown(Key.ALT); type("d"); keyUp(Key.ALT)  # create and move new copy
    type(".2"); type(Key.TAB)
    type("1"); type(Key.TAB)
    type(".5"); type(Key.ENTER)
    keyDown(Key.SHIFT); click(); keyUp(Key.SHIFT)  # add first object to selection
    click("collider_convex_make_convex.png"); hover(Pattern("3dview_collider_multiple_convex_created.png").exact())
    type(Key.ESC + "x" + Key.ENTER)  # remove convex
    type(Key.ESC + "a");  # make sure everything is selected
    click("collider_convex_convert_to_loc.png"); wait(Pattern("3dview_collider_multiple_convex_loc_created.png").exact(), 1.5)
    click("collider_convex_mesh_to_convex_op_header.png"); click("collider_convex_delete_original_geo_2.png")
    click("collider_convex_individual_objects.png"); wait(Pattern("3dview_collider_multiple_convex_loc_created_individual.png").exact(), 1.5)
    click("collider_convex_delete_original_geo.png")
    click(Pattern("3dview_collider_multiple_convex_loc_created_2.png").exact().targetOffset(89,-117)); type(Key.ESC + "x" + Key.ENTER)  # delete selected upper object
    click(Pattern("3dview_collider_convex_loc_created_wire.png").exact())
    click("collider_convex_convert_to_mesh.png"); find(Pattern("3dview_collider_convex_created_wire.png").exact())
    click("collider_convex_convert_to_loc.png"); find(Pattern("3dview_collider_convex_loc_created_wire_2.png").exact())
except:
    scs_bt_configurator.save_screenshot(getBundlePath(), Screen())
    raise
finally:
    scs_bt_configurator.close_blender(p)