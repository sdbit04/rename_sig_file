import os
import shutil
import argparse


def read_neinfo(reference):
    reference = os.path.abspath(reference)
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


def rename_sig_file(input_folder, reference_file):
    reference_file = reference_file
    abs_input_folder = os.path.abspath(input_folder)
    list_files = os.listdir(abs_input_folder)
    reference_map = read_neinfo(reference_file)
    print(reference_map)
    os.chdir(abs_input_folder)
    for file in list_files:
        if file.endswith((".SIG", ".SIG.gz")) and "NE=" in file:
            print("file name is {}".format(file))
            file_name_items = file.split(".", maxsplit=1)
            try:
                replacement = reference_map[file_name_items[0]]
            except KeyError:
                print("No reference found in neinfo.dat for {0}, skipping this file {1}".format(file_name_items[0], file))
            else:
                new_file_name = "{0}.{1}".format(replacement, file_name_items[1])
                print("{0} -vs- {1}".format(file, new_file_name))
                shutil.move(file, new_file_name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="provide input_dir, and reference file path")
    parser.add_argument("input_folder", help="Provide input folder path as first argument")
    parser.add_argument("reference_file", help="Please provide the path of reference file")
    args = parser.parse_args()
    # input_folder = r"D:\D_drive_BACKUP\MENTOR\yubaraj\Rename_sig\input"
    # reference_file = r"D:\D_drive_BACKUP\MENTOR\yubaraj\Rename_sig\neinfo.dat"
    input_folder = args.input_folder
    reference_file = args.reference_file
    rename_sig_file(input_folder, reference_file)

