#!/usr/bin/env python3

from sys import argv
from datetime import datetime  # To use the time functionality
import os  # To interact with the os
import ntpath  # To interact with the filepath
import shutil  # High level file operations (cp img)

def get_commandline_input():
    file_path = argv[1]
    if os.path.exists(file_path):

        args = len(argv)
        regex = '<>:"|?*'

        #the only argument that should be accepted is the file path
        if(args > 2):
            print("You have entered too many arguments. Please enter only one filepath.")
        #if there is no argument, tell the user to enter a file path
        elif(args == 1):
            print("Please enter a file path")
        #file path must not be greater than 247 characters
        elif(len(file_path) > 247):
            print("File path is too long")

        #iterate over the characters in regex and check if they are in the file path
        for i in regex:
            if i in file_path:
             print("File path cannot contain <>:|?*")
        else:
            return file_path
    else:
        print("File does not exist")
        return False

def check_fileType(fileName):
    if fileName[-4:] in {'.jpg', '.png', '.img', '.gif'}:
        return True
    else:
        print("Please enter a file name with a .jpg, .png, .img, or .gif extension")
 
def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)
 
def create_base_directory():
    desktop = os.path.normpath(os.path.expanduser("~/Desktop")) #Get path to the Desktop
    base_path = desktop + "/AGR/Graphs/"
    if os.path.exists(base_path):
        return base_path
    else:
        try:
            os.makedirs(base_path)  #Create all necessary directories
        except OSError:
            print ("Creation of the directory %s failed" % base_path)
        else:
            return base_path
            print ("Successfully created the directory %s" % base_path)
            
def create_image_folder(base_path, file_path):
    print("image")
    
    if os.path.getsize(file_path) < 1000000:
        
        og_file_name = path_leaf(file_path)
        if check_fileType(og_file_name):
            now = datetime.now()
            timestamp = str(round(datetime.timestamp(now)))
            new_file_name = og_file_name + "." + timestamp  #Create the file name
            image_path = base_path + "/" + new_file_name
            try:
                os.mkdir(image_path)  #Create all necessary directories
            except OSError:
                print ("Creation of the directory %s failed" % image_paths)
            else:
                print ("Successfully created the directory %s" % image_path)
                f = open(image_path + "/" + new_file_name + ".json", 'w')  #Create .json file

    else:
        print("File is too large, must be less than 1 MB")
        
def main():
    file_path = get_commandline_input()
    if not file_path:
        quit()
    else:
        print("file path is ", file_path)
        base_path = create_base_directory()
        print("base path is ", base_path)
        create_image_folder(base_path, file_path)
    

    
main()
