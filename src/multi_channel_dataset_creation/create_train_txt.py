import os
import argparse
import pathlib
import overlap
import time
import sys

def print_overwrite(text):
    """
    Writing to the same line again and again
    """
    # Get the width of the console (assuming a fixed width font)
    console_width = 100  # You may need to adjust this based on your terminal/console width

    # Pad the text with spaces to the right to clear the entire line
    padded_text = text.ljust(console_width)

    sys.stdout.write('\r' + padded_text)
    sys.stdout.flush()

def create_train_txt(path_to_all_txt,path_to_valid_txt,path_to_all_images,path_to_valid_images,remove_overlapping_images=False,name_prefix="" ):
    """
    create a train.txt file based on all.txt and valid.txt
    files presetn in valid.txt should not be present in train.txt
    files(geotifs) overlapping with the files(geotifs) in valid.txt ,should not be present in train.txt
    @returns: path_to_created_train_txt_file
    """

    create_train_txt_start = time.time()

    path_to_all_txt= pathlib.Path(path_to_all_txt)
    path_to_valid_txt = pathlib.Path(path_to_valid_txt)
    path_to_train_txt = path_to_all_txt.parents[0]/ (name_prefix+"train.txt")
    train_files=[] #all files not present in valid.txt
    images_overlapping_with_images_in_validationset = []


    with open(path_to_all_txt,"r") as all_file:
        all_lines =  [line.strip() for line in all_file.readlines()]
    with open(path_to_valid_txt,"r") as valid_file:
        valid_lines =  [line.strip() for line in valid_file.readlines()]

    #for all files in teh dataset (all.txt)
    nr_of_files = len(all_lines)
    finnished_file = 0
    for filename in all_lines:
        found_file = False
        found_overlapping_file = False
        #compare it to each file in valid.txt
        for validset_filename in valid_lines:

            #file in all.txt is present in valid.txt and should therfore not be present in train.txt
            if validset_filename in filename:
                found_file = True
                break
            if remove_overlapping_images:
                # file in all.txt is overlapping with file in valid.txt and should therfore not be present in train.txt
                if overlap.geotiff_overlap(str(pathlib.Path(path_to_valid_images)/validset_filename), str(pathlib.Path(path_to_all_images)/filename)):
                    found_overlapping_file= True
                    images_overlapping_with_images_in_validationset.append(filename)
                    break

        if (not found_file) and (not found_overlapping_file):
            train_files.append(filename)

        finnished_file+=1
        time_per_image = (time.time() - create_train_txt_start)/finnished_file
        print_overwrite("create train.txt processed :"+str(finnished_file)+ " out of :"+str(nr_of_files)+ " estimated time left : "+str((time_per_image* (nr_of_files-finnished_file))/60)+ " minutes")

    print() #go to a new line since the last print did not do this
    print("overlaping files:")
    print(images_overlapping_with_images_in_validationset)

    print("found : "+str(len(images_overlapping_with_images_in_validationset)) +" files that not were present in valid.txt but overlapped with files in valid.txt")
    print("creating train.txt took: "+str((time.time()-create_train_txt_start)/60) + ", minutes")

    #write the lines to train.txt
    with open(path_to_train_txt,"w") as train_file:
        train_file.write("\n".join(train_files))
    return path_to_train_txt

if __name__ == "__main__":
    # Initialize parser
    parser = argparse.ArgumentParser()

    parser.add_argument("-v", "--Validtxtfile", help="path to .txt file that includes the validation images",
                        required=True)
    parser.add_argument("-a", "--Alltxtfile",
                        help="path to .txt file that includes all images for training and validation", required=True)
    parser.add_argument("-p", "--Prefix", help="prefix for the train.txt file  . e.g  test ->  test_train.txt",
                        required=False)

    parser.add_argument("-i", "--path_to_all_images",
                        help="path to teh folder where the all.txt images are stored", required=True)
    parser.add_argument("-j", "--path_to_valid_images",
                        help="path to teh folder where the valid.txt images are stored", required=True)
    parser.add_argument('--remove_overlapping', action='store_true', default=False)





    args = parser.parse_args()

    if args.Prefix:
        train_trefix = args.Prefix
    else:
        train_trefix =""


    
    create_train_txt(path_to_all_txt=args.Alltxtfile,path_to_valid_txt=args.Validtxtfile,path_to_all_images= args.path_to_all_images,path_to_valid_images= args.path_to_valid_images,remove_overlapping_images=args.remove_overlapping,name_prefix=train_trefix)
