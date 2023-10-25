load("scs_bt_configurator.jar")

def switch_to_default():
    click(Pattern("looks_entries_2.png").exact().targetOffset(-15,-12))

def switch_to_default_01():
    click(Pattern("looks_entries_1.png").exact().targetOffset(-11,13))

import scs_bt_configurator
p = scs_bt_configurator.start_it_up(getBundlePath(), "looks.blend")
try:
    wait(Pattern("startup.png").similar(0.98),5)
    click(Pattern("diffuse_black.png").exact())
    click(Pattern("color_widget_hsv.png").similar(0.85).targetOffset(-54,-34)); click(Pattern("color_widget_rgb.png").similar(0.85).targetOffset(-8,12)); type("1" + Key.ENTER); find(Pattern("green_view.png").similar(0.98))
    switch_to_default(); find(Pattern("startup.png").similar(0.98))
    switch_to_default_01(); find(Pattern("green_view.png").similar(0.98))
    click(Pattern("diffuse_green.png").targetOffset(71,1)); type(Key.ENTER)  # open write trough menu and confirm
    switch_to_default(); find(Pattern("green_view.png").similar(0.98))
except:
    scs_bt_configurator.save_screenshot(getBundlePath(), Screen())
    raise
finally:
    scs_bt_configurator.close_blender(p)