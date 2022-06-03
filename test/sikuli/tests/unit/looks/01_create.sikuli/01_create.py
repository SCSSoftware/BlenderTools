load("scs_bt_configurator.jar")
import scs_bt_configurator
p = scs_bt_configurator.start_it_up(getBundlePath(), "looks.blend")
try:
    wait(Pattern("startup.png").exact(),5)
    region = find(Pattern("looks_panel.png").exact())
    region.click(Pattern("add_remove_buttons.png").exact().targetOffset(0,-11))
    mouseMove(-50, 0)  # move mouse away to remove hover button effect
    region.click(Pattern("add_remove_buttons.png").exact().targetOffset(0,-11))
    find(Pattern("startup.png").exact())
    region.find(Pattern("look_entries.png").exact())
except:
    scs_bt_configurator.save_screenshot(getBundlePath(), Screen())
    raise
finally:
    scs_bt_configurator.close_blender(p)