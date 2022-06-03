In order to properly run tests for SCS Blender Tools you first need to
configure SikuliX IDE properly. After installing it you need to add
"scs_bt_configurator" extension to it and properly edit scs_bt_config.ini.
For more information about scs_bt_config.ini open it and read comments.


How to install "scs_bt_configurator":
=====================================================================
You need to copy "scs_bt_configurator.jar" and "scs_bt_config.ini" to SikuliX extensions folder.
* On linux to: ~/.Sikulix/Extensions
* On Windows: %APPDATA%\Sikulix\Extensions


How to rebuild and install "configurator" (Linux):
=====================================================================
If you made some changes to configurator you can rebuild it with 
"install_configurator.sh". It will pack configurator in jar file used by 
SikuliX, then it will copy newly created jar and config file for you.
Usage example:
bash install_configurator.sh

NOTE: you need to have installed file-roller package otherwise script
will fail.
