Usage:
rename_sig_file.exe "Parent_Input_dir_containing_daily_directory" "path of neinfo.dat file" --content_type tar/sig

Functionality:
This process will find all the directories under Parent-directory provided as first argument.
If --content_type is provided as "tar" or nothing, then the process will find all the tar files under the child or Daily directories.
Extract them, rename the .sig files based on neinfo.dat as a reference. finally delete those .tar files.

If --content_type is provided as "sig", then it rename the sig files under Daily directories.


Assumption:
Program has been written based on the Directory structure below:
    Input_directory:
        --Daily_dir1:
            -- files1.tar
            -- files2.tar
        --Daily_dir2:
            --file3.tar
            --file4.tar

