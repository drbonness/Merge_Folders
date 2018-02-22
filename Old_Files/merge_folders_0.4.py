import os
import csv
import re
from tkinter import filedialog
from tkinter import *
import time
import filecmp
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

# Example:

#   dir1 = 'C:\Python\My Code\DB\File Merging\Testing\Test Folder 1'
#   dir2 = 'C:\Python\My Code\DB\File Merging\Testing\Test Folder 2'
#   dest = 'C:\Python\My Code\DB\File Merging\Testing\Dest Folder'

top_level = []
start = 0
            
def get_top_level():
    
    global top_level

    start = time.clock()

    if(os.path.isdir(dir_location[0]) and
       os.path.isdir(dir_location[1]) and
       os.path.isdir(dir_location[2])):        

        top_level = [dir_location[0].rsplit('\\',1)[-1],
                     dir_location[1].rsplit('\\',1)[-1],
                     dir_location[2].rsplit('\\',1)[-1]]

        merge(dir_location[0], dir_location[1], dir_location[2])
        # Ex: top_level = ['Test Folder 1', 'Test Folder 2', 'Dest Folder']

        # Recall the "start" variable to measure elapsed time
        elapsedsec = round((time.clock() - start),2)
        elapsedmin = round((elapsedsec/60),2)
        elapsedhours = round((elapsedmin/60),2)

        if elapsedsec < 60:
            elapsed_time = (str(elapsedsec) + ' seconds.')
        elif elapsedsec > 60 and elapsedmin < 60:
            elapsed_time = (str(elapsedmin) + ' minutes.')
        else:
            elapsed_time = (str(elapsedhours) + ' hours.')

        print('Merging completed in %s' % (elapsed_time))  

# Takes three inputs: Two directories to compare, and destination directory
def merge(dir1, dir2, dest):

    global top_level

    output_text.set('Merging Directories:\n' + shortenPath(dir1)
                    + '\n and \n ' + shortenPath(dir2))    

    # Get the current path, starting from our directory folders
    current_path = dir1.rsplit(top_level[0],1)[1]

    # Define "compared" as the general directory comparison
    compared = filecmp.dircmp(dir1, dir2)
    

    for file in compared.left_only: # All files unique to dir1
        if os.path.isfile(os.path.join(dir1, file)):
            print('%s found in %s.' % (file, top_level[0]))
            # Copy all of them over to dest directory
            shutil.copyfile(os.path.join(dir1, file), os.path.join(dest, file))

    for folder in compared.left_only: # All folders unique to dir1
        if os.path.isdir(os.path.join(dir1, folder)):
            print('Unique folder %s found in %s.' % (folder, top_level[0]))
            # Copy all contents to dest directory
            shutil.copytree(os.path.join(dir1, folder),
                            os.path.join(dest, folder))

    # NOTE: copytree fails if the destination directory already exists.
    # Proposed solutions here: https://stackoverflow.com/questions/1868714/how-do-i-copy-an-entire-directory-of-files-into-an-existing-directory-using-pyth
            
        
    for file in compared.right_only: # All files unique to dir2
        if os.path.isfile(os.path.join(dir2, file)):
            print('%s found in %s.' % (file, top_level[1]))
            # Copy all of them over to dest directory
            shutil.copyfile(os.path.join(dir2, file), os.path.join(dest, file))

    for folder in compared.right_only: # All folders unique to dir2
        if os.path.isdir(os.path.join(dir2, folder)):
            print('Unique folder %s found in %s.' % (folder, top_level[1]))
            # Copy all contents to dest directory
            shutil.copytree(os.path.join(dir2, folder),
                            os.path.join(dest, folder))

        
    for file in compared.common_files: # All files that appear in both dirs
        if os.path.isfile(os.path.join(dir1, file)):
            
            if filecmp.cmp(os.path.join(dir1, file), os.path.join(dir2, file)):
                print('Identical copies of %s found in both directories.'
                      % file)
                # Copy the file over
                shutil.copyfile(os.path.join(dir1, file),
                                os.path.join(dest, file))
            else:
                print('Different copies of %s found in both directories.'
                      % file)
                # Rename and then copy both files over
                file1 = file[:-4] + '_' + dir1_entry.get() + file[-4:]
                file2 = file[:-4] + '_' + dir2_entry.get() + file[-4:]
                shutil.copyfile(os.path.join(dir1, file),
                                os.path.join(dest, file1))
                shutil.copyfile(os.path.join(dir2, file),
                                os.path.join(dest, file2))

    for folder in compared.common_dirs: # All folders that appear in both dirs

        # Create those shared folders in our master directory
        try:
            os.makedirs(os.path.join(dest, folder))
            print('%s folder created in destination directory.'
                  % (folder))
            
        # Unless they already exist    
        except FileExistsError:
            print('%s already exists in destination directory.'
                  % (folder))
            pass

        # Dive into each one and start over
        # print('Recursing!')
        merge(os.path.join(dir1, folder),
              os.path.join(dir2, folder),
              os.path.join(dest, folder))


def test_stuff():

    dir1_name = dir1_entry.get()
    dir2_name = dir2_entry.get()
    dest_name = dest_entry.get()

    print(dir1_name)
    print(dir2_name)
    print(dest_name)

    for i in range(10):
        time.sleep(0.1)
        output_text.set('blah'*i)

################################################################################
#                                                                              #
################################################################################

# tkinter GUI 

root = Tk()
root.title("Merge Folders 0.4")
root.geometry("400x420")
root.grid_columnconfigure(1, weight=1)

dir1_text = str
dir2_text = str
dir3_text = str
path_display = [StringVar(), StringVar(), StringVar()]
dir_location = ["","",""]

try:
    updatePath(0, csv_text[0][0])
    updatePath(1, csv_text[0][1])
    updatePath(2, csv_text[0][2])
except:
    pass

output_text = StringVar()

path_1_button = Button(root, text="Choose Path", command=lambda : choosePath(0))
path_2_button = Button(root, text="Choose Path", command=lambda : choosePath(1))
dest_button   = Button(root, text="Choose Path", command=lambda : choosePath(2))
merge_button = Button(root, text="Merge Directories",
                      command=lambda : get_top_level(), font=("TkDefaultFont",16))
test_button = Button(root, text="Test",
                      command=lambda : test_stuff(), font=("TkDefaultFont",16))


Label(root,text="File Copy Verification",font=("TkDefaultFont",20)).grid(row=0, columnspan = 2)
Label(root,text="Directory 1:",font=("TkDefaultFont",16)).grid(row=1, sticky=W)
Label(root,text="Directory 2:",font=("TkDefaultFont",16)).grid(row=3, sticky=W)
Label(root,text="Destination",font=("TkDefaultFont",16)).grid(row=5, sticky=W)

dir1_entry = Entry(root, bd=2, width=5, exportselection=0,
                   textvariable = dir1_text)
dir2_entry = Entry(root, bd=2, width=5, exportselection=0,
                   textvariable = dir2_text)
dest_entry = Entry(root, bd=2, width=20, exportselection=0,
                   textvariable = dir3_text)
dir1_entry.insert(0,'A')
dir2_entry.insert(0,'B')
dest_entry.insert(0,'Merged Folders')

path_label_1 = Label(root, textvariable=path_display[0],anchor=E)
path_label_2 = Label(root, textvariable=path_display[1],anchor=E)
dest_label = Label(root, textvariable=path_display[2],anchor=E)
path_label_1.config(relief="solid",borderwidth=1)
path_label_2.config(relief="solid",borderwidth=1)
dest_label.config(relief="solid",borderwidth=1)

output_label = Label(root, textvariable=output_text)

dir1_entry.grid(row=1, column=1, padx=5, sticky=W)
dir2_entry.grid(row=3, column=1, padx=5, sticky=W)
dest_entry.grid(row=5, column=1, padx=5, sticky=W)

path_1_button.grid(row=2)
path_2_button.grid(row=4)
dest_button.grid(row=6)
merge_button.grid(row=7, columnspan=2, pady=3)
test_button.grid(row=8, columnspan=2, pady=3)

path_label_1.grid(row=2,column=1,padx=5,sticky=EW)
path_label_2.grid(row=4,column=1,padx=5,sticky=EW)
dest_label.grid(row=6,column=1,padx=5,sticky=EW)

output_label.grid(row=9,columnspan=2)

root.mainloop()
