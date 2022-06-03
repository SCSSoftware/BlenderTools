Sikuli tests folder consists of tests for SCS Blender Tools
which can be executed by SikuliX IDE.


How to execute specific test:
=====================================================================
After opening SikuliX IDE just try to open test with File -> Open...
(Make sure you selected directory with sikuli test or *.sikuli file)


How to execute more tests at once in Linux:
=====================================================================
For advanced testing of more tests at once you can use "run_tests.sh"
bash script if there is any in directory you want to test from.
This script expects one argument which specify JAR file
of the SikuliX IDE .

Example of running:
> cd ~/sikuli/tests/unit
>
> bash run_tests.sh ~/Programs/sikulixide-2.0.5.jar


NOTE: run_tests.sh tries to execute scripts in all children
directories if there is "run_tests.sh" file)


