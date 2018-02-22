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
#                               THE MERGE ZONE                                 #
################################################################################

top_level = []
            
def get_top_level():

    master = dir_location[0]
    
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

    # Alert user to current activity
    changetext('Current Directory:\n' + shortenPath(dir2))    

    compared = filecmp.dircmp(dir1, dir2) # General directory comparison

    ''' STEP 1: Copy over unique files/folders '''               
    for item in compared.right_only: # Everything unique to dir2 (by name)
        
        if os.path.isfile(os.path.join(dir2, file)): # Unique files
            print('%s found in %s.' % (item, top_level[1]))
            # Copy all of them over to dest directory
            shutil.copyfile(os.path.join(dir2, item), os.path.join(dir1, item))

        elif os.path.isdir(os.path.join(dir2, item)): # Unique folders
            print('Unique folder %s found in %s.' % (item, top_level[1]))
            # Copy all contents to dest directory
            shutil.copytree(os.path.join(dir2, item), os.path.join(dir1, item))

    ''' STEP 2: Rename and copy over files with unique contents '''
    for file in compared.diff_files: # All shared files with different contents

        # Rename and then copy files from dir2 to dir1
        newfile = rename(file, '_' + str(rootnum))
        shutil.copyfile(os.path.join(dir2, file), os.path.join(dir1, newfile))

    ''' STEP 3: Root out impostor duplicates and delete them ''' 
    suspects = compared.diff_files  # Suspected imposters
    dir1_files = []                 # All files in dir1
    dir1_renamed = []               # All renamed files (includes '_#' string)

    for file in os.listdir(dir1):
        if os.path.isfile(os.path.join(dir1, file)):
            dir1_files.append(file)            
            matches = []
            numregex = re.compile(r'_\d+.')
            matches = numregex.findall(file)
            if len(matches) != 0:
                dir1_renamed.append(file)

    dir1_renamed_stripped = strip(dir1_renamed) # All renamed files, minus '_#'
    
    for suspect in suspects: # Loop through all suspects
                       
        indices = [i for i, x in enumerate(dir1_renamed_stripped)
                   if x == suspect] # Get indices of suspect
        
        suspect_matches = []
        for index in indices: # Using indices, get list of matches
            suspect_matches.append(dir1_renamed[index])
            
        suspect_pairs = []
        for pair in combinations(suspect_matches, 2): # Generate list of tuples
            suspect_pairs.append(pair)

        for n in range(len(suspect_pairs)): # Compare each pair

            file0 = os.path.join(dir1, suspect_pairs[n][0])
            file1 = os.path.join(dir1, suspect_pairs[n][1])

            if filecmp.cmp(file0, file1): # Duplicate found
                try:
                    os.remove(file0) # Try to delete
                except:
                    pass # Already deleted

    ''' STEP 4: Repeat steps 1-4 all the way down '''
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
            
    return stripped # = 'blahblah.txt'
        
def changetext(text): # Clear the output text and replace with given string
    
    output_text.set('                                                       ' +
                    '                                                       ' +
                    '                                                       ' )
    root.update_idletasks()
    output_text.set(str(text))
    root.update_idletasks()    

def test_stuff():

    for i in range(5):
        for j in range(6):
            changetext('Loading.' + '.'*j)
            time.sleep(0.2)

    '''icons = ['|', '/', '--','\\']
    for i in range(10):
        for symbol in icons:
            changetext('Loading... ' + symbol)
            time.sleep(0.2)'''
    
    '''for i in range(15):
        time.sleep(0.1)
        changetext('blah'*i)'''
        
################################################################################
#                                                                              #
################################################################################

# Tkinter GUI 

root = Tk()
root.title("Merge Folders 0.6")
root.geometry("400x240")

dir_text = str
path_display = [StringVar()]
dir_location = [""]

try:
    updatePath(0, csv_text[0][0])
except:
    pass

output_text = StringVar()

path_button = Button(root, text="Choose Path", command=lambda : choosePath(0))

merge_button = Button(root, text="Merge Directories",
                      command=lambda : get_top_level(), font=("TkDefaultFont",16))
test_button = Button(root, text="Test",
                      command=lambda : test_stuff(), font=("TkDefaultFont",16))

Label(root,text="File Copy Verification",
      font=("TkDefaultFont",20)).place(x=65, y=5)

Label(root,text="Directory:",
      font=("TkDefaultFont",16)).place(x=20, y=45)

path_label = Label(root, textvariable=path_display[0],anchor=E)
path_label.config(relief="solid",borderwidth=1)

output_label = Label(root, textvariable=output_text)

path_button.place(x=25, y=75)
merge_button.place(x=40, y=115)
test_button.place(x=260, y=115)
path_label.place(x=125, y=52)
output_label.place(x=35, y=170)

root.mainloop()
