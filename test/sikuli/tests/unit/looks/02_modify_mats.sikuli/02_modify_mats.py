import configurator, subprocess
reload(configurator)
p = configurator.start_it_up(getBundlePath(), "looks.blend")

def switch_to_default():
    click(Pattern("looks_entries_2.png").similar(0.92).targetOffset(-15,-12))

def switch_to_default_01():
    
    click(Pattern("looks_entries_1.png").similar(0.92).targetOffset(-11,13))
            
try:
    wait(Pattern("startup.png").similar(0.91),5)
    find(Pattern("diffuse_attr.png").similar(0.92)).right().click(Pattern("diffuse_color.png").similar(0.94))
    click(Pattern("rgb.png").similar(0.91)); type("1" + Key.ENTER); find(Pattern("green_view.png").similar(0.91))
    switch_to_default(); find(Pattern("startup.png").similar(0.91))
    switch_to_default_01(); find(Pattern("green_view.png").similar(0.91))
    find(Pattern("diffuse_attr.png").similar(0.92)).right().click(Pattern("wt.png").similar(0.95))
    switch_to_default(); find(Pattern("green_view.png").similar(0.91))
except:
    configurator.save_screenshot(getBundlePath(), Screen())
    raise
finally:
    configurator.close_blender(p)