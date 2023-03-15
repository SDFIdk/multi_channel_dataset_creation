#Some ML projects for emantic segmetnation e.g mask-dino assumes that the training data and validation data are in training and validation folders
#This script use train.txt and valid.txt files for copying all iamges to this format.

import os
import pathlib
import shutil
def copy_files_to_folder(text_file,origin_folder,destination_folder):
    """
    :param text_file:
    :param origin_folder:
    :param destination_folder:
    :return:
    """
    origin_folder = pathlib.Path(origin_folder)
    destination_folder = pathlib.Path(destination_folder)
    os.makedirs(destination_folder, exist_ok = True)
    with open(text_file) as f:
        lines= f.readlines()

        files = [origin_folder/line.rstrip() for line in lines if os.path.isfile(origin_folder/line.rstrip())]
    print("copying the images noted in " +str(text_file)+ " from :"+str(origin_folder) +" to "+str(destination_folder) +"...")
    for file in files:
        shutil.copy2(file, destination_folder/file.name)
    print("done copying the images noted in " +str(text_file)+ " from :"+str(origin_folder) +" to "+str(destination_folder) )



def copy_to_train_and_valid_folders(origin_folder,train_folder,valid_folder,train_txt,valid_txt):
    copy_files_to_folder(train_txt,origin_folder,train_folder)
    copy_files_to_folder(valid_txt,origin_folder,valid_folder)

if __name__ == "__main__":
    example_usage= r"python copy_files.py "
    print("########################EXAMPLE USAGE########################")
    print(example_usage)
    print("#############################################################")
    import argparse

    # Initialize parser
    parser = argparse.ArgumentParser()

    parser.add_argument("-t", "--Train_text_file", help="path/to/train.txt ",required=True, type=pathlib.Path)
    parser.add_argument("-v", "--Valid_text_file", help="path/to/valid.txt ",required=True,type=pathlib.Path)
    parser.add_argument("-l", "--LabelFolder", help="path/to/folder  e.g path/to/masks",required=True,type=pathlib.Path)
    parser.add_argument("-i", "--ImageFolder", help="path/to/folder  e.g path/to/images",required=True,type=pathlib.Path)

    #images are copied to the folders validation and training
    parser.add_argument("--Valid_folder_name", help="folder name e.g validation",default = "validation", required=False)
    parser.add_argument("--Training_folder_name", help="folder name e.g training",default = "training", required=False)

    #labels are copied to annotations/training and annotations/validation
    parser.add_argument("--New_label_folder", help="folder name e.g annotations",default = "annotations", required=False)



    args = parser.parse_args()

    print("copying images")
    copy_files_to_folder(text_file=args.Valid_text_file,origin_folder=args.ImageFolder,destination_folder= args.ImageFolder.parent/args.Valid_folder_name)
    copy_files_to_folder(text_file=args.Train_text_file,origin_folder=args.ImageFolder,destination_folder= args.ImageFolder.parent/args.Training_folder_name)

    print("copying labels")
    copy_files_to_folder(text_file=args.Valid_text_file,origin_folder=args.LabelFolder,destination_folder= args.LabelFolder.parent/args.New_label_folder/args.Valid_folder_name)
    copy_files_to_folder(text_file=args.Train_text_file,origin_folder=args.ImageFolder,destination_folder= args.LabelFolder.parent/args.New_label_folder/args.Training_folder_name)
