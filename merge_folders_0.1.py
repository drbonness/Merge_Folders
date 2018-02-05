import os
import csv
import re
from tkinter import filedialog
from filecmp import dircmp
from tkinter import *
import shutil

# Path Functions

def choosePath(path_num):
    path = filedialog.askdirectory()
    if(path is not ""):
        updatePath(path_num, path)
        writeCSV([dir_location])
    
def updatePath(path_num, path):
    dir_location[path_num] = path
    path_display[path_num].set(shortenPath(path))
    
def shortenPath(path):
    split_path = re.split('/',path)
    path_text = ""
    
    if(len(split_path)>5):
        path_text = str(split_path[2]+"/"+
                    split_path[3]+
                    "/.../"+
                    split_path[len(split_path)-2]+"/"+
                    split_path[len(split_path)-1]) # input directory
    else:
        path_text = path
    
    return path_text

# Directories

def compareDir():
    if(os.path.isdir(dir_location[0]) and os.path.isdir(dir_location[1])):
        output = is_same(dir_location[0], dir_location[1])
        if(output):
            output_text.set("True - Directory Contents Are Equal")
        else:
            output_text.set("False - Directory Contents Are Not Equal")
    else:
        output_text.set("Failure - Could Not Open Folders")
        
def is_same(dir1, dir2):
    
    # Compare two directory trees content. Return False if they differ,
    # True if they are the same.
    
    compared = dircmp(dir1, dir2,[".DS_Store"])
    if (compared.left_only or compared.right_only or compared.diff_files 
        or compared.funny_files):
        return False
    for subdir in compared.common_dirs:
        if not is_same(os.path.join(dir1, subdir), os.path.join(dir2, subdir)):
            return False
    return True
        
# CSV Files
    
def writeCSV(output_list):
    file = open(config_filename,"w")
    for x in range(len(output_list)):
        file.seek(0);
        csv_writer = csv.writer(file, delimiter=',', quotechar='"')
        csv_writer.writerow(output_list[x])

# Saving last search to .csv
 
config_filename = "setup.config" # input configuration filename
csv_text = []

if(os.path.isfile(config_filename)):   # check it's a file
    config_file = open(config_filename,"r") # input configuration file
    csv_text = list((csv.reader(config_file, delimiter=',', quotechar='"')))


################################################################################
#                               THE MG ZONE                                    #
################################################################################


# Returns generator of all files in a directory, as strings (excludes folders)
def files(path):
    for file in os.listdir(path):
        if os.path.isfile(os.path.join(path,file)):
            yield file

# Returns generator of all folders in a directory, as strings (excludes files)
def folders(path): 
    for folder in os.listdir(path):
        if not os.path.isfile(os.path.join(path,folder)):
            yield folder

# Save the very top level of our file structure for later use
def get_top_level(dir1, dir2, dest):
    
    global top_level

    top_level = [dir1.rsplit('\\',1)[-1],
                 dir2.rsplit('\\',1)[-1],
                 dest.rsplit('\\',1)[-1]]

    # Ex: top_level = ['Test Folder 1', 'Test Folder 2', 'Dest Folder']

    # testdir = 'C:\Python\My Code\DB\File Merging\Testing\Test Folder 1
    #           \we can go deeper\even deeper'

    # testdir.rsplit(top_level[0],1)

    # ['C:\\Python\\My Code\\DB\\File Merging\\Testing\\',
    # '\\we can go deeper\\even deeper']

    # Using this method we can get everything before and after our current
    # working directory in the absolute path.
    
    compare(dir1, dir2, dest)
    

# Takes three inputs: Two directories to compare, and destination directory
def compare(dir1, dir2, dest):

    global top_level

    for file1 in files(dir1):
        for file2 in files(dir2):
        """ Loop through all files, see if they exist in other directory """

            filename1 = os.fsdecode(file1)  #Ex: 'bruh.txt'
            filename2 = os.fsdecode(file2)
            
            # Same name, same contents
            if filecmp.cmp(filename1,filename2):
                copy(filename1)
            
            # Same name, different contents
            else:
                if filename1 == filename2:
                    # Rename files
                    os.rename(os.path.abspath(filename1),
                              filename1[:-4] + '_A')
                    os.rename(os.path.abspath(filename2),
                              filename2[:-4] + '_B')

                    # Copy both files to new master directory
                    copy(filename1[:-4] + '_A')
                    copy(filename2[:-4] + '_B')

                # Different names, different contents
                else:
                    # Copy both files to new master directory
                    copy(filename1)
                    copy(filename2)

    

    # For each shared folders at this level:
    for shared_folder in filecmp.dircmp(dir1, dir2).common_dirs:

        # Create those shared folders in our master directory

        # Dive into each one and start over
        compare(os.path.join(dir1, shared_folder),
                os.path.join(dir2, shared_folder), dest)


def copy(filename):
    
    global file_list
    
    """ Copy the given file to a new master directory, and add it to a list so
        that we can keep track of which ones we've moved over. """

    # Copy file to new master directory
    shutil.copy(os.path.abspath(filename), 'destination')

def createfolder(folder, path):

    """ Create a folder with the given name in the master directory at the
        given path. """
    
    os.makedirs(

################################################################################
#                                                                              #
################################################################################

# tkinter GUI 

root = Tk()
root.title("Verify Copy")
root.geometry("400x250")
root.grid_columnconfigure(1, weight=1)

path_display = [StringVar(), StringVar()]
dir_location = ["",""]

try:
    updatePath(0, csv_text[0][0])
    updatePath(1, csv_text[0][1])
except:
    pass

output_text = StringVar()

path_1_button = Button(root, text="Choose Path", command=lambda : choosePath(0))
path_2_button = Button(root, text="Choose Path", command=lambda : choosePath(1))
compare_button = Button(root, text="Compare Directories",
                        command=lambda : compareDir(),font=("TkDefaultFont",16))

Label(root,text="File Copy Verification",font=("TkDefaultFont",20)).grid(row=0, columnspan = 2)
Label(root,text="Directory 1",font=("TkDefaultFont",16)).grid(row=1, sticky=W)
Label(root,text="Directory 2",font=("TkDefaultFont",16)).grid(row=3, sticky=W)

path_label_1 = Label(root, textvariable=path_display[0],anchor=E)
path_label_2 = Label(root, textvariable=path_display[1],anchor=E)
path_label_1.config(relief="solid",borderwidth=1)
path_label_2.config(relief="solid",borderwidth=1)

output_label = Label(root, textvariable=output_text);

path_1_button.grid(row=2)
path_2_button.grid(row=4)
compare_button.grid(row=5,columnspan = 2,pady=10)

path_label_1.grid(row=2,column=1,padx=5,sticky=EW)
path_label_2.grid(row=4,column=1,padx=5,sticky=EW)

output_label.grid(row=6,columnspan = 2)

root.mainloop()
