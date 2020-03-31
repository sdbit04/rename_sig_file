import os
import shutil
import argparse
import tarfile


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


def rename_sig_file(input_folder, reference_file, out_dir=None):
    # The input_folder of this method will take only .SIG or .SIG.gz files
    reference_file = reference_file
    abs_input_folder = os.path.abspath(input_folder)
    list_files = os.listdir(abs_input_folder)
    reference_map = read_neinfo(reference_file)
    # print(reference_map)
    os.chdir(abs_input_folder)
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
                print("{0} -vs- {1}".format(file, new_file_name))
                if out_dir is None:
                    shutil.move(file, new_file_name)
                else:
                    out_file = os.path.abspath(os.path.join(out_dir, new_file_name))
                    shutil.move(file, out_file)
    os.chdir("{}\\..".format(abs_input_folder))


def rename_sig_inside_tar(input_folder_contain_tar_gz, reference_file, content_type='tar'):
    input_folder_contain_tar_gz = os.path.abspath(input_folder_contain_tar_gz)
    reference_file = os.path.abspath(reference_file)
    os.chdir(input_folder_contain_tar_gz)
    tar_file_list = os.listdir(input_folder_contain_tar_gz)
    for file_name in tar_file_list:
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
                rename_sig_file(internal_temp_dir, reference_file, input_folder_contain_tar_gz)

                try:
                    shutil.rmtree(internal_temp_dir)
                except PermissionError:
                    pass
        else:
            if content_type.lower() == 'sig':
                rename_sig_file(input_folder_contain_tar_gz, reference_file)


def main():
    parser = argparse.ArgumentParser(description="provide input_dir, and reference file path")
    parser.add_argument("input_folder", help="Provide input folder path as first argument")
    parser.add_argument("reference_file", help="Please provide the path of reference file")
    parser.add_argument("content_type", help="Please mentioned if the input-folder contain sig, or tar")
    print("Help contact : swapankumar.das@teoco.com")
    args = parser.parse_args()
    input_folder = args.input_folder
    reference_file = args.reference_file
    content_type = args.content_type
    for cur_dir, list_dir, list_files in os.walk(input_folder):
        if content_type is None or content_type == "tar":
            rename_sig_inside_tar(cur_dir, reference_file)
        else:
            rename_sig_inside_tar(cur_dir, reference_file, content_type)
        for dir in list_dir:
            print("dir under current directory is {}".format(dir))
            abs_dir = os.path.abspath(os.path.join(cur_dir, dir))
            if content_type is None:
                rename_sig_inside_tar(abs_dir, reference_file)
            else:
                rename_sig_inside_tar(abs_dir, reference_file, content_type)


if __name__ == "__main__":
    main()
