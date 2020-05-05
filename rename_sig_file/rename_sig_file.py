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


def rename_sig_file_list(list_files, reference_map, out_dir):
    for file in list_files:
        if file.endswith((".SIG", ".SIG.gz")) and "NE=" in file:
            print("file name is {}".format(file))
            file_name_items = file.split(".", maxsplit=1)
            try:
                replacement = reference_map[file_name_items[0]]
            except KeyError:
                print(
                    "No reference found in neinfo.dat for {0}, skipping this file {1}".format(file_name_items[0], file))
            else:
                new_file_name = "{0}.{1}".format(replacement, file_name_items[1])
                print("Old= {0} -vs- New= {1}".format(file, new_file_name))
                if out_dir is None:
                    shutil.move(file, new_file_name)
                else:
                    out_file = os.path.abspath(os.path.join(out_dir, new_file_name))
                    shutil.move(file, out_file)


def rename_sig_files_in_a_dir(input_folder, reference_map, out_dir=None):
    # The input_folder of this method will take only .SIG or .SIG.gz files
    """
    reference_file = reference_file

    reference_map = read_neinfo(reference_file)
    """
    # print(reference_map)
    abs_input_folder = os.path.abspath(input_folder)
    list_files = os.listdir(abs_input_folder)
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
    os.chdir(abs_input_folder)
    print("Present directory is {}".format(abs_input_folder))
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


    th = 0
    for thread in thread_list:
        print("running thread = {}".format(th))
        thread.start()
        # Main thread will proceed and delete the input folder, so we should pause input folder until all threads complete
        thread.join()
        th += 1
    os.chdir("{}\\..".format(abs_input_folder))


def rename_sig_inside_tar(input_folder_contain_tar_gz, reference_map, content_type='tar'):
    input_folder_contain_tar_gz = os.path.abspath(input_folder_contain_tar_gz)
    os.chdir(input_folder_contain_tar_gz)
    # START
    tar_file_list = os.listdir(input_folder_contain_tar_gz)
    for file_name in tar_file_list:
        # REMOVE which are not a tar.gz file
        if not file_name.endswith(".tar.gz"):
            tar_file_list.remove(file_name)
    if len(tar_file_list) != 0:
        internal_temp_dir = os.path.join(input_folder_contain_tar_gz, "TEMP")
        # os.mkdir(internal_temp_dir, 777)
        print("List of tar file is {}".format(tar_file_list))
        for file in tar_file_list:
            if file.endswith("tar.gz"):
                abs_file = os.path.join(input_folder_contain_tar_gz, file)
                tf = tarfile.open(abs_file)
                tf.extractall(internal_temp_dir)
                tf.close()
                print("Working on {}".format(file))
                rename_sig_files_in_a_dir(internal_temp_dir, reference_map, input_folder_contain_tar_gz)
                print("Working done on file {}".format(file))
                try:
                    shutil.rmtree(internal_temp_dir)
                except PermissionError:
                    pass
        else:
            if content_type.lower() == 'sig':
                rename_sig_files_in_a_dir(input_folder_contain_tar_gz, reference_map)


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
        if content_type is None or content_type == "tar":
            rename_sig_inside_tar(cur_dir, reference_map)
        else:
            rename_sig_inside_tar(cur_dir, reference_map, content_type)
        for dir in list_dir:
            print("dir under current directory is {}".format(dir))
            abs_dir = os.path.abspath(os.path.join(cur_dir, dir))
            if content_type is None:
                rename_sig_inside_tar(abs_dir, reference_map)
            else:
                rename_sig_inside_tar(abs_dir, reference_map, content_type)


if __name__ == "__main__":
    main()
