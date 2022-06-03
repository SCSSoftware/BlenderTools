# Script will run all the sikuli tests in current directory
# and expects 1 argument as path to installed Sikuli IDE.
# Additionaly second argument "skip_reset" can be passed which will
# cancel searching and executing *reset_blender.sikuli test
#
# Usage examples:
#
# -> Running directly in console:
#  ./run_tests.sh ~/Programs/Sikuli
#
# -> Running and writing to log file:
#  ./run_tests.sh ~/Programs/Sikuli > ~/Work/BlenderTools/Testing/BlenderTestsOutput/sikuli.log

# try to find reset_blender.sikuli test and run it
red='\e[0;31m'
green='\e[0;32m'
nc='\e[0m'

if [[ $2 != skip_reset ]]; then
   reset_dir="*reset_blender.sikuli"
   depth=10
   while [ $(find $reset_dir -maxdepth 0 -type d | wc -l) -ne 1 ] || [ $depth = 0 ]; do
      reset_dir="../"$reset_dir
      depth=$(($depth-1))
   done
   #if reset not found or if it is in current directory don't execute it
   if [ $depth -ne 0 ] && [ $depth -ne 10 ]; then
      CWD=$(pwd)
      cd $(find $reset_dir -maxdepth 0 -type d)
      cd ..
      for dir in *.sikuli ; do
         echo -e "$red--> Running reset test!$nc"
         java -jar $1 -r "$dir"
         i=$((i+1))
         echo -e "$red--> Done!\n$nc"
      done
      cd $CWD
   fi
fi

tests_count=$(find *.sikuli -maxdepth 0 -type d | wc -l)
i=1
for dir in * ; do
   if [ -d "$dir" ]; then #for each directory
      if  [[ $dir == *.sikuli ]]; then #if directory ends with .sikuli then run it
         echo -e "$nc--> Running test $i/$tests_count: $dir"
         java -jar $1 -r "$dir"
         i=$((i+1))
         echo -e "--> Done!\n"
      else #otherwise check if within directory exists run_tests.sh and run it
         cd $dir
         if [ -f "run_tests.sh" ]; then
            echo -e "$green\n--> Entering directory: '$dir'$nc"
            bash run_tests.sh $1 skip_reset
            echo -e "$green--> Quiting directory: '$dir'!$nc"
         fi
         cd ..
      fi
   fi
done

