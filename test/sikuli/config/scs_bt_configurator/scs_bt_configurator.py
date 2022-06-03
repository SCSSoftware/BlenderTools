from sikuli import *
import os
import shutil
import signal
import subprocess
import ConfigParser


def __get_config_ini_path():
    splited_dir = (os.path.dirname(__file__), "")
    for _ in range(2):
        splited_dir = os.path.split(splited_dir[0])
    return os.path.join(splited_dir[0], "scs_bt_config.ini")


def __get_output_subpath(test_path):
    """
    Tries to find "tests" in given path and returns semipath from tests to test_path
    """
    path_to_module = ""
    splited_curr_dir = os.path.split(test_path)
    # try to find root "tests" folder otherwise output will be written directly to 'OutputPath'
    if "tests" in splited_curr_dir[0]:
        splited_dir = os.path.split(splited_curr_dir[0])
        while "tests" in splited_dir[0]:
            path_to_module = os.path.join(splited_dir[1], path_to_module)
            splited_dir = os.path.split(splited_dir[0])
    return path_to_module


def __get_startup_command(bundle_path, blend_file):
    """
    Returns startup command for Blender with given blend file.
    When executed command will run Blender on location 0,800 with size 1000,888 and will output
    it's console buffer to directory which is configured in config.ini.
    "config.ini" must have section "PATHS" with variables: "BlenderPath" and "OutputPath"
    """
    if not os.path.isdir(bundle_path):
        curr_dir = os.path.dirname(bundle_path)
    else:
        curr_dir = bundle_path

    splited_curr_dir = os.path.split(curr_dir)

    blender_path = get_path_property('BlenderPath')
    output_path = get_path_property('OutputPath')

    output_path = os.path.join(output_path, __get_output_subpath(curr_dir))

    if not os.path.exists(output_path):  # make sure that output path exists
        os.makedirs(output_path)
    else:  # if already exists purge old files of current test
        for file in os.listdir(output_path):
            if splited_curr_dir[1] in file:
                os.remove(os.path.join(output_path, file))

    log_file = os.path.join(output_path, splited_curr_dir[1] + ".log")
    blend_file = os.path.join(curr_dir, blend_file)

    return [blender_path, blend_file, "-p", "0", "800", "1000", "800"], log_file


def get_path_property(property_name):
    """
    Returns value of requested property from PATHS section from "config.ini" file.
    "config.ini" must have section "PATHS" with given property name
    """
    config = ConfigParser.ConfigParser()
    config.read(__get_config_ini_path())  # from folder of config.jar load config.ini
    return os.path.expanduser(config.get('PATHS', property_name))


def start_it_up(bundle_path, blend_file, delete_pix=True):
    """
    Starts blender with given file in subprocess. If delete_pix argument is given as False
    it won't delete all old pix files within test directory.
    Returns started subprocess and log file handle as list: [subprocess.Popen, log_handle].
    """
    if delete_pix:  # delete all pix files by default
        for file in os.listdir(bundle_path):
            if file[-4:-1] == ".pi":
                os.remove(os.path.join(bundle_path, file))
                print("[log] -> PIX file removed: " + file)
        scs_base = get_path_property("SCSBasePath")
        if not os.path.exists(scs_base):  # make sure that scs base path exists
            os.makedirs(scs_base)
        else:
            for file in os.listdir(scs_base):
                if file[-4:-1] == ".pi":
                    os.remove(os.path.join(scs_base, file))
                    print("[log] -> PIX file removed: " + file)

    start_cmd, log_file = __get_startup_command(bundle_path, blend_file)
    log = open(log_file, 'w')
    print("[log] -> Starting blender with cmd: %r" % start_cmd)
    return [subprocess.Popen(start_cmd, stdout=log, stderr=log), log]


def close_blender(process_with_log):
    # move to save location and make sure to close any possible error popups
    hover(Location(450, 400))
    type(Key.ESC)

    # properly close Blender now and finish process
    keyDown(Key.CTRL)
    type("q")
    keyUp(Key.CTRL)
    # Don't Save changes
    hover(Location(400, 400))
    type("d")
    finish_process(process_with_log)


def finish_process(process_with_log):
    """
    Waits for given process to finish and properly closes the log file.
    Argument should be a list with elements: [subprocess.Popen, log_handle]
    """
    p = process_with_log[0]
    log = process_with_log[1]
    log_file = log.name
    p.wait()
    log.flush()
    log.close()
    print("[log] -> Log file and process properly closed!")

    # since sikuli won't catch any possible python errors,
    # analyze output file now as it's closed

    has_log_with_error = False
    with open(log_file, "r") as f:
        for line in f.readlines():
            if line.find("Traceback (most recent call last):") != -1:
                has_log_with_error = True
                break

    if has_log_with_error:
        raise Exception("Script finished with python errors in blender log file, checkout result at: '%s'!" % log_file)


def save_screenshot(bundle_path, screen):
    """
    Creates screenshot of blender area within given screen and saves it to output directory.
    """
    file = screen.capture(0, 0, 1050, 850).save()  # only capture blender area defined in get_startup_command

    if not os.path.isdir(bundle_path):
        curr_dir = os.path.dirname(bundle_path)
    else:
        curr_dir = bundle_path

    splited_curr_dir = os.path.split(curr_dir)
    output_path = get_path_property('OutputPath')
    output_path = os.path.join(output_path, __get_output_subpath(curr_dir))

    shutil.move(file, os.path.join(output_path, splited_curr_dir[1] + os.path.splitext(file)[1]))
    print("[log] -> Screenshot saved!")


def delete_scs_tools_config():
    """
    Deletes config.txt file within SCS Blender Tools directory
    """
    scs_tools_path = get_path_property("SCSToolsPath")
    for file in os.listdir(scs_tools_path):
        if "config.txt" in file:
            os.remove(os.path.join(scs_tools_path, file))
            print("[log] -> SCS tools config.txt successfully deleted!")
            break
