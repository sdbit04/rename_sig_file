import os
import shutil
import argparse
import tarfile
from threading import *


def read_neinfo(reference):
    reference = os.path.realpath(reference)
    reference_map = {}
    with open(reference) as reference_ob:
        for line in reference_ob.readlines():
            line_items = line.split("?")
            for item in line_items:
                if "NE=" in item:
                    NE_index = line_items.index(item)
                    NE_name_index = NE_index + 1
                    reference_map[line_items[NE_index].strip()] = line_items[NE_name_index].strip()
    return reference_map


def rename_sig_file_list(abs_input_folder, list_files, reference_map, out_dir=None):
    """Most Granular method
    This method will be called once you have a list of .Sig files to be worked on
    """
    for file in list_files:
        if file.upper().endswith((".SIG", ".SIG.GZ")) and "NE=" in file.upper():
            file_path = os.path.join(abs_input_folder, file)
            print("file name is {}".format(file_path))
            # print("{}-{}".format( file, os.path.exists(file_path)))
            file_name_items = file.split(".", maxsplit=1)
            try:
                replacement = reference_map[file_name_items[0]]
            except KeyError:
                print(
                    "No reference found in neinfo.dat for {0}, skipping this file {1}".format(file_name_items[0], file))
            else:
                new_file_name = "{0}.{1}".format(replacement, file_name_items[1])
                print("Old= {0} -vs- New= {1}".format(file, new_file_name))
                # print("{}-{}".format(file, os.path.exists(file_path)))
                if out_dir is None:
                    new_file_path = os.path.join(abs_input_folder, new_file_name)
                    shutil.move(file_path, new_file_path)
                else:
                    out_file = os.path.abspath(os.path.join(out_dir, new_file_name))
                    shutil.move(file_path, out_file)


def rename_sig_files_in_a_dir(input_folder, reference_map, out_dir=None):
    # The input_folder of this method will take only .SIG or .SIG.gz files
    """
    This method will be called once you got a directory having only Sig files
    """
    # print(reference_map)
    abs_input_folder = os.path.abspath(input_folder)
    # os.chdir(abs_input_folder)
    list_files = os.listdir(abs_input_folder)
    print("Sig file list at {} = {}".format(abs_input_folder, list_files))
    # thread_for_a_file = Thread(target=rename_one_sig_file)
    """
    I have file list with me : []
    As discussed, it is good to have max 6 threads.
    if files_count <= 6:
        number of thread = file_count
        number of files per thread = 1
    else:
        number of thread = 6
        number of files per thread for 5 threads = files_count//5 # I have kept one thread in hand to handle remaining files
        number of files for 6th thread = file_count mod 5 # We can easy understand the file_count in 6th thread is less then the other threads, so we are good.
    """
    # print("Present directory is {}".format(abs_input_folder))
    rename_sig_file_list(abs_input_folder, list_files, reference_map, out_dir)
    """ # Removing multi threading from here 
    thread_list = []
    file_count = len(list_files)
    print("Total number of files {}".format(file_count))
    max_threads_count = 6
    if file_count <= max_threads_count:
        total_threads = file_count
        print("File per thread is decided = 1")
        for i in range(total_threads): # 0 .... 5
            thread_list.append(Thread(target=rename_sig_file_list, args=(list_files[i], reference_map, out_dir)))
    else:
        total_threads = max_threads_count
        files_per_threads_for_5_threads = file_count // (max_threads_count - 1)
        file_for_last_thread = file_count % (max_threads_count - 1)
        print("File per thread is decided = {}".format(files_per_threads_for_5_threads))
        for i in range(total_threads):
            thread_list.append(Thread(target=rename_sig_file_list, args=(list_files[i*files_per_threads_for_5_threads:i+files_per_threads_for_5_threads], reference_map, out_dir)))
            thread_list.append(Thread(target=rename_sig_file_list, args=(list_files[-file_for_last_thread:], reference_map, out_dir)))
    print("Threads are {}".format(thread_list))
    th = 0
    for thread in thread_list:
        print("running thread = {}".format(th))
        thread.start()
        th += 1
        # Main thread will proceed and delete the input folder, so we should pause input folder until all threads complete
        thread.join()
        """
    # We want to delete the temp folder to stored extract of .tar, so we need to leave the temp directory.
    # os.chdir("{}\\..".format(abs_input_folder))


def rename_sig_file_into_tar_list(tar_file_list, reference_map, input_folder_contain_tar_gz):
    """This method will be called once I have got a list of .tar files
    """
    for file in tar_file_list:
        if file.endswith("tar.gz"):
            # Decide a temp-directory for each .tar file
            temp_dir = str(file).split(".")[0]
            print("Temp dir for tar {} is {}".format(str(file), temp_dir))
            internal_temp_dir = os.path.join(input_folder_contain_tar_gz, temp_dir)
            abs_file = os.path.join(input_folder_contain_tar_gz, file)
            tf = tarfile.open(abs_file)
            print("Extracting {} file ".format(file))
            tf.extractall(internal_temp_dir)  # this dir to be made based on thread ID
            tf.close()
            print("Working on {}".format(file))
            try:
                rename_sig_files_in_a_dir(internal_temp_dir, reference_map, input_folder_contain_tar_gz)
            except:
                print("Working on {} was failed ".format(file))
            else:
                print("Working done on file {}, so deleting it, and its corresponding temp dir {}".format(file, internal_temp_dir))
                try:
                    shutil.rmtree(internal_temp_dir)
                    os.remove(abs_file)
                except PermissionError:
                    pass


def rename_sig_inside_tars_under_base_dir(input_folder_contain_tar_gz, reference_map, content_type='tar'):
    input_folder_contain_tar_gz = os.path.abspath(input_folder_contain_tar_gz)
    os.chdir(input_folder_contain_tar_gz)
    # START
    tar_file_list = os.listdir(input_folder_contain_tar_gz)
    sig_file_list = []
    for file_name in tar_file_list:
        # REMOVE which are not a tar.gz file
        if not file_name.endswith(".tar.gz"):
            tar_file_list.remove(file_name)
            if file_name.upper().endswith(".SIG") or file_name.upper().endswith(".SIG.GZ"):
                sig_file_list.append(file_name)

    print("Sig file list : {}".format(sig_file_list))

    if content_type.lower() == "tar":
        ##### Single thread ##############
        # rename_sig_file_into_tar_list(tar_file_list, reference_map, input_folder_contain_tar_gz)
        #################################
        ##### Multi Thread ##############
        if len(tar_file_list) != 0:
            # os.mkdir(internal_temp_dir, 777)
            print("List of tar file is {}".format(tar_file_list))
            ##########################
            thread_list = []
            tar_file_count = len(tar_file_list)
            print("Total number of tar files {}".format(tar_file_count))
            max_threads_count = 6
            if tar_file_count <= max_threads_count:
                total_threads = tar_file_count
                print("File per thread is decided = 1")
                for i in range(total_threads):  # 0 .... 5
                    thread_list.append(Thread(target=rename_sig_file_into_tar_list, args=([tar_file_list[i]], reference_map, input_folder_contain_tar_gz)))
            else:
                total_threads = max_threads_count
                files_per_threads_for_5_threads = tar_file_count // (max_threads_count - 1)
                file_for_last_thread = tar_file_count % (max_threads_count - 1)
                print("File per thread is decided = {}".format(files_per_threads_for_5_threads))
                for i in range(total_threads): # 0 to 5
                    if i <= 4:
                        thread_list.append(Thread(target=rename_sig_file_into_tar_list, args=(tar_file_list[i*files_per_threads_for_5_threads: i*files_per_threads_for_5_threads+ files_per_threads_for_5_threads], reference_map, input_folder_contain_tar_gz)))
                    else:
                        thread_list.append(Thread(target=rename_sig_file_into_tar_list, args=(tar_file_list[-file_for_last_thread:], reference_map, input_folder_contain_tar_gz)))
            print("Threads are {}".format(thread_list))

            th_nbr = 0
            for thread in thread_list:
                thread.start()
                print(th_nbr)
                th_nbr += 1

            for thread in thread_list:
                thread.join()
        else:
            print("No .tar file to process in {}".format(input_folder_contain_tar_gz))
    elif content_type.lower() == "sig" or content_type.lower() == "sig.gz":
        sig_thread_list = []
        max_thread_count = 6
        sig_files_count = len(sig_file_list)
        if sig_files_count > 0:
            if sig_files_count <= max_thread_count:
                total_thread_count = sig_files_count
                sig_files_per_thread = 1
                for thread_id in range(0, total_thread_count, sig_files_per_thread):
                    sig_thread_list.append(Thread(target=rename_sig_file_list, args=(input_folder_contain_tar_gz, [sig_file_list[thread_id]], reference_map)))
            else:
                total_thread_count = max_thread_count
                sig_files_per_thread_for_5_threads = sig_files_count // (max_thread_count-1)
                sig_files_for_6th_thread = sig_files_count % (max_thread_count-1)
                for sig_file_id in range(0,(sig_files_count-sig_files_for_6th_thread), sig_files_per_thread_for_5_threads):
                    sig_thread_list.append(Thread(target=rename_sig_file_list, args=(input_folder_contain_tar_gz, sig_file_list[sig_file_id:sig_file_id+sig_files_per_thread_for_5_threads, reference_map])))
                sig_thread_list.append(Thread(target=rename_sig_file_list, args=(input_folder_contain_tar_gz, sig_file_list[-sig_files_for_6th_thread:], reference_map)))


def main():
    parser = argparse.ArgumentParser(description="provide input_dir, and reference file path")
    parser.add_argument("input_folder", help="Provide input folder path as first argument")
    parser.add_argument("reference_file", help="Please provide the path of reference file")
    parser.add_argument("-c", "--content_type", help="Please mentioned if the input-folder contain sig, or tar")
    print("Help contact : swapankumar.das@teoco.com")
    args = parser.parse_args()
    input_folder = args.input_folder
    reference_file = args.reference_file
    reference_map = read_neinfo(reference_file)
    content_type = args.content_type
    print("content type is {}".format(content_type))
    for cur_dir, list_dir, list_files in os.walk(input_folder):
        print("Current directory is {}".format(cur_dir))
        for dir in list_dir:
            abs_dir = os.path.join(cur_dir, dir)
            if content_type is None:
                rename_sig_inside_tars_under_base_dir(abs_dir, reference_map)
            else:
                rename_sig_inside_tars_under_base_dir(abs_dir, reference_map, content_type=content_type)


if __name__ == "__main__":
    main()
