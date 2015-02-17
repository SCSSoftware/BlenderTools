
SCS Blender Tools
=================

SCS Blender Tools are official tools for model and asset creation for
trucking games by SCS Software. You can download actual version free
of charge using GitHub repository "https://github.com/SCSSoftware/BlenderTools".

Blender is multi-platform Open Source application for 3D content creation
and you can download it free of charge on "http://www.blender.org".


What tools are included:
------------------------
 - SCS mid-format importer
 - SCS mid-format exporter
 - Multi-object system
 - Part/Variant system
 - Special Locators
 - SCS Material system (using shader presets)
 - Special tool-shelf with additional tools


Installation:
-------------
All the files needed for tools installation are contained within "addon"
directory in a single folder named "io_scs_tools". 
This folder must be placed in a location, where Blender can find it and 
read it as an Addon. It is possible to use an installation method, 
where you can just point Blender to the Addon location
(e.g. if you want to run the tools right from GIT repository).

You can use one the following installation possibilities:

1. LOCAL INSTALLATION:
   Place the folder "io_scs_tools" to your installation of Blender to
   a location "<Blender_installation>\<version_number>\scripts\addons\". 
   The Addon will be used only by this particular installation of Blender.
2. GLOBAL INSTALLATION:
   Place the folder "io_scs_tools" in your profile to the location
   "<user_profile>\blender\<version_number>\scripts\addons\".
   Addon will be used by any Blender installation of specified version.
3. INSTALLATION TO THE USER DIRECTORY:
   In "User Preferences" within "File" section is the "Scripts" item
   where you can set the path to any Addon location. This way, for
   example, you can use any Addon directly from data repository and your
   tools will always be of the current version in all of your Blender
   installations. It is necessary, that the Addon folder was placed inside
   a folder named "addons_contrib" and Blender needs to be directed to its
   parent folder. Therefore the resulting path to the folder Addons should
   look like "<folder>\addons_contrib\io_scs_tools", but the path under
   Scripts will only be "<folder>".
4. INSTALL FROM FILE:
   Tools can also be installed using the "Install from File..." button,
   which you can find in "User Preferences" in the "Addons" section on the
   bottom bar.

NOTE: For more information see "Blender’s Configuration & Data Paths" at:
"http://wiki.blender.org/index.php/Doc:2.6/Manual/Introduction/Installing_Blender/DirectoryLayout"


Notes:
------
 - In case of trouble installing SCS Blender Tools make sure you're using
   compatible Blender version. SCS Blender Tools for Blender versions
   prior 2.73 are not supported.


Help, questions, troubleshooting:
---------------------------------
If you encounter any problems or have questions regarding SCS Blender Tools,
please visit "Blender Tools" forum at "http://forum.scssoft.com" and 
don't hesitate to ask if your problem wasn't addressed already. Also
don't miss the wiki ("https://github.com/SCSSoftware/BlenderTools/wiki")
for many useful tips and docs.


Bugs:
-----
For reporting bugs please visit our forum at "http://forum.scssoft.com" and
go to "Blender Tools > Bugs" sub-forums.


License:
--------
SCS Blender Tools are developed and distributed under GNU GPL v3.
http://www.gnu.org/licenses/gpl-3.0.html


SCS Blender Tools Team

