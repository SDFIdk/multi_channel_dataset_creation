import os
import argparse
import pathlib
import shutil
if __name__ == "__main__":
    """
    copy files from a folder to another 
    gives the files new names by replacing part of its name with a new string
    
    if your code assumes that all data sources and labels have the same name for the same area this script is handy to use for changing the names to the correct format
    """



    usage_example="example usage: \n "+r"python rename_files.py --inputfolder path\to\folder --outputfolder path\to\folder --replacestring originalstring --newstring newstring"
    # Initialize parser
    parser = argparse.ArgumentParser(
        epilog=usage_example,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-i", "--inputfolder", help="path\to\folder",required=True)
    parser.add_argument("-o", "--outputfolder", help="path\to\folder",required=True)
    parser.add_argument("-r", "--replacestring", help="e.g original_image",required=True)
    parser.add_argument("-n", "--newstring", help="e.g new_image_copy",required=True)
    args = parser.parse_args()

    files = os.listdir(args.inputfolder)
    for (index,file) in enumerate(files):
        print("working on file :"+str(index) + " out of :"+str(len(files)))
        input_path = pathlib.Path(args.inputfolder)/pathlib.Path(file)
        output_path = pathlib.Path(args.outputfolder)/pathlib.Path(file.replace(args.replacestring,args.newstring))
        shutil.copy2(input_path,output_path)
