load("scs_bt_configurator.jar")

def switch_to_default():
    click(Pattern("looks_entries_2.png").exact().targetOffset(-15,-12))

def switch_to_default_01():
    click(Pattern("looks_entries_1.png").exact().targetOffset(-11,13))

import scs_bt_configurator
p = scs_bt_configurator.start_it_up(getBundlePath(), "looks.blend")
try:
    wait(Pattern("startup.png").exact(),5)
    click(Pattern("diffuse_black.png").exact())
    click(Pattern("color_widget_hsv.png").exact().targetOffset(-54,-34)); click(Pattern("color_widget_rgb.png").exact().targetOffset(-8,12)); type("1" + Key.ENTER); find(Pattern("green_view.png").exact())
    switch_to_default(); find(Pattern("startup.png").exact())
    switch_to_default_01(); find(Pattern("green_view.png").exact())
    click(Pattern("diffuse_green.png").targetOffset(71,1)); type(Key.ENTER)  # open write trough menu and confirm
    switch_to_default(); find(Pattern("green_view.png").exact())
except:
    scs_bt_configurator.save_screenshot(getBundlePath(), Screen())
    raise
finally:
    scs_bt_configurator.close_blender(p)