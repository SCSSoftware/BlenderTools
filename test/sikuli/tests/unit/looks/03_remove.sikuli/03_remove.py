import configurator, subprocess
reload(configurator)
p = configurator.start_it_up(getBundlePath(), "looks.blend")

try:
    wait(Pattern("startup.png").similar(0.91),5)
    click(Pattern("add_remove_buttons.png").similar(0.93).targetOffset(3,9)); find(Pattern("green_view.png").similar(0.91))
except:
    configurator.save_screenshot(getBundlePath(), Screen())
    raise
finally:
    configurator.close_blender(p)