import os
import shutil

input_folder = r"D:\D_drive_BACKUP\MENTOR\yubaraj\Rename_sig\input"
reference_file = r"D:\D_drive_BACKUP\MENTOR\yubaraj\Rename_sig\neinfo.dat"


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
    os.chdir(abs_input_folder)
    for file in list_files:
        if file.endswith((".SIG", ".SIG.gz")) and "NE=" in file:
            print("file name is {}".format(file))
            file_name_items = file.split(".", maxsplit=1)
            replacement = reference_map[file_name_items[0]]
            new_file_name = "{0}.{1}".format(replacement, file_name_items[1])
            print("{0} -vs- {1}".format(file, new_file_name))
            shutil.move(file, new_file_name)


if __name__ == "__main__":
    rename_sig_file(input_folder, reference_file)


