load("scs_bt_configurator.jar")
import scs_bt_configurator
p = scs_bt_configurator.start_it_up(getBundlePath(), "looks.blend")
try:
    wait(Pattern("3dview_first_look.png").similar(0.98),5)
    click(Pattern("looks_entries.png").exact().targetOffset(-3,10)); wait(Pattern("3dview_second_look.png").exact())
    click("export_selected_button.png")
    wait(1); type(Key.ESC)
    hover(Pattern("3dview_second_look.png").exact());
    type("2")  # switch to 2nd collection
    type(Key.F3 + "SCS Import" + Key.ENTER)  # do import
    hover(Pattern("new_folder_button.png").exact()); mouseMove(50, 0); paste(scs_bt_configurator.get_path_property("SCSBasePath"))
    wait(0.1); click(Pattern("game_object_pim.png").similar(0.95)); type(Key.ENTER)
    wait(Pattern("3dview_first_look.png").similar(0.97))
    click(Pattern("looks_entries.png").exact().targetOffset(-3,10));
    wait(Pattern("3dview_second_look.png").similar(0.97))
except:
    scs_bt_configurator.save_screenshot(getBundlePath(), Screen())
    raise
finally:
    scs_bt_configurator.close_blender(p)