
import re

file1 = 'butts.txt'
file2 = 'butts_sheet.xlsx'
file3 = 'corrup...ted_b_1ut_9ts.abcdefg'
file4 = 'toomanycooks.wmv'

newfile1 = 'butts_1.txt'
newfile2 = 'butts_sheet_8.xlsx'
newfile3 = 'corrup...ted_b_331.ut_19.ts_55.abcdefg'
newfile4 = 'toomanycooks_999.wmv'

decoyuno = 'bats.txt_A'
decoydos = 'boughts.xlsx'

myfiles = [newfile1, newfile2, newfile3, newfile4, decoyuno, decoydos]


def rename(filename): # Rename files; add '_1' before file extension

    suffix = '.' + filename.rsplit('.')[-1]
    prefix = filename[:(len(filename)-len(suffix))]
    newfilename = prefix + '_1' + suffix
    print(newfilename)

rename(file1)
rename(file2)
rename(file3)
rename(file4)


def strip(filelist): # Remove '_n'

    matches = []
    numregex = re.compile(r'_\d+.')

    # Ex: file = 'blahblah_2.txt'
    for file in filelist:
        matches = numregex.findall(file)    # = ['_2.']
        if len(matches) != 0:
            numsuffix = matches[-1]         # = '_2.'
            index = file.rfind(numsuffix)   # = 8
            print('File: ' + file)
            prefix = file[:index]           # = 'blahblah'
            suffix = file[(index + len(numsuffix)):] # = '.txt'
            file = prefix + '.' + suffix
            print('Stripped file: ' + file + '\n')


strip(myfiles)
