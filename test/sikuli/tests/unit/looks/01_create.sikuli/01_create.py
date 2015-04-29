import configurator, subprocess
reload(configurator)
p = configurator.start_it_up(getBundlePath(), "looks.blend")

try:
    wait(Pattern("startup.png").similar(0.91),5)
    region = find(Pattern("add_remove_buttons.png").similar(0.91))
    region.click(Pattern("add_remove_buttons.png").similar(0.91).targetOffset(2,-10))
    region.click(Pattern("add_remove_buttons.png").similar(0.91).targetOffset(2,-10))

    find(Pattern("startup.png").similar(0.91))
    find(Pattern("look_entries.png").similar(0.91))

except:
    configurator.save_screenshot(getBundlePath(), Screen())
    raise
finally:
    configurator.close_blender(p)