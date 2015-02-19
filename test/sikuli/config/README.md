In order to properly run tests for SCS Blender Tools you first need to
configure Sikuli IDE properly. After installing it you need to add
"configurator" extension to it and properly edit config.ini.
For more information about config.ini open it and read comments.


How to install "configurator":
=====================================================================
You need to copy "configurator-1.0.jar" and "config.ini" to Sikuli extensions folder.
On linux to: ~/.sikuli/extensions
On Windows: %APPDATA%\Sikuli\extensions


How to rebuild and install "configurator" (Linux):
=====================================================================
If you made some changes to configurator you can rebuild it with 
"install_configurator.sh". It will pack configurator in jar file used by 
Sikuli, then it will copy newly created jar and config file for you.
Usage example:
bash install_configurator.sh

NOTE: you need to have installed file-roller package otherwise scirpt
will fail
