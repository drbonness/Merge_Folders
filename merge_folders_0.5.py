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

#   master = 'C:\Python\My Code\DB\File Merging\Testing\master'

top_level = []
start = 0
            
def get_top_level(master):
    
    global top_level

    start = time.clock()

    if os.path.isdir(master):
        # Save the names of our root folders, and make full paths out of them
        root_names = os.listdir(master) # = ['1', '2', '3',...]
        for i in range(len(root_names)):
            top_level[i] = os.path.join(master, root_names[i])

        # Copy the first root folder and append it to the top_level list
        shutil.copytree(top_level[0], os.path.join(master, 'Merge'))
        top_level.append(os.path.join(master, 'Merge'))

        # Merge all folders, beginning with entries 1 and -1
        for rootnum in range(1, len(top_level)):
            merge(top_level[-1], top_level[rootnum])
        
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

# Takes two inputs: First directory (future master) and directory to compare
def merge(dir1, dir2):

    global top_level

    # Alert user to current activity
    output_text.set('Merging Directories:\n' + shortenPath(dir1)
                    + '\n and \n ' + shortenPath(dir2))    

    # Define "compared" as the general directory comparison
    compared = filecmp.dircmp(dir1, dir2)   

    # NOTE: copytree fails if the destination directory already exists.
    # Proposed solutions here: https://stackoverflow.com/questions/1868714/how-do-i-copy-an-entire-directory-of-files-into-an-existing-directory-using-pyth
                    
    for item in compared.right_only: # Everything unique to dir2 (by name)
        
        if os.path.isfile(os.path.join(dir2, file)): # Unique files
            print('%s found in %s.' % (item, top_level[1]))
            # Copy all of them over to dest directory
            shutil.copyfile(os.path.join(dir2, item), os.path.join(dir1, item))

        elif os.path.isdir(os.path.join(dir2, item)): # Unique folders
            print('Unique folder %s found in %s.' % (item, top_level[1]))
            # Copy all contents to dest directory
            shutil.copytree(os.path.join(dir2, item), os.path.join(dir1, item))


    for file in compared.diff_files: # All shared files with different contents

        # Rename and then copy files from dir2 to dir1
        newfile = rename(file, '_' + str(rootnum))
        shutil.copyfile(os.path.join(dir2, file), os.path.join(dir1, newfile))

################################################################################
   
    old_dupes = [] # All files in dir1 with a suffix like: '_#.'
    dir1files = [] # All files in dir1

    for file in os.listdir(dir1):
        if os.path.isfile(os.path.join(dir1, file)):
            dir1files.append(file)            
            matches = []
            numregex = re.compile(r'_\d+.')
            matches = numregex.findall(file)
            if len(matches) != 0:
                old_dupes.append(file)
                          
    stripped_old = strip(dir1files) # old_dupes minus the suffixes
    stripped_new = strip(compared.diff_files) # new dupes minus the suffixes

    if len(stripped_dupes) != 0: # Were there any old_dupes?

        # Did we copy anything over up above that matches a stripped file?
        shared = list(set(stripped_old) & set(stripped_new))

        if len(shared) != 0: # Yes, now we have to find their indexes

            filepairs = [] # All files to be double checked for dupes

            for file in range(len(shared)):                
                filepairs.append(
                    old_dupes[stripped_old.index(shared[file])])
                filepairs.append(
                    stripped_new[stripped_new.index(shared[file])])

            for pair in combinations(myfiles, 2): # Make some pairs
                filepairs.append(pair)

            deleted = []

            for n in range(len(filepairs)):

                file0 = os.path.join(dir1, filepairs[n][0])
                file1 = os.path.join(dir1, filepairs[n][1])

                if filecmp.cmp(file0, file1):
                    print('%s and %s are the same file.' %
                          (filepairs[n][0], filepairs[n][1]))
                    # If we haven't already, delete one and add name to list
                    try:
                        deleted.index(file0)
                    except:
                        os.remove(os.path.join(dir1, file0))
                        deleted.append(file0)

################################################################################
                                     

    for folder in compared.common_dirs: # All folders that appear in both dirs

        # Dive into each one and start over
        merge(os.path.join(dir1, folder), os.path.join(dir2, folder))

def rename(filename, suffix): # Ex: filename = butts.txt, suffix = '_1'

    extension = '.' + filename.rsplit('.')[-1]
    prefix = filename[:(len(filename)-len(extension))]
    newfilename = prefix + str(suffix) + extension
    return newfilename # Ex: newfilename = butts_1.txt

def strip(filelist): # Remove '_n'

    matches = []
    stripped = []
    numregex = re.compile(r'_\d+.')

    # Ex: file = 'blahblah_2.txt'
    for file in filelist:
        matches = numregex.findall(file)    # = ['_2.']
        if len(matches) != 0:
            numsuffix = matches[-1]         # = '_2.'
            index = file.rfind(numsuffix)   # = 8
            prefix = file[:index]           # = 'blahblah'
            suffix = file[(index + len(numsuffix)):] # = '.txt'
            file = prefix + '.' + suffix
            stripped.append(file)
            
    return stripped

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
