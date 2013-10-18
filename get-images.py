# search for folders on seeley server, copy over missing files from Images

# change 'get' dirs if cloud


import os
import csv
import datetime
import math

now = datetime.datetime.now()
time = now.strftime("%Y%m%d_%H-%M")

# helper functions
def dateSL2Images(date):
    return date[0:4] + "-" + date[4:6] + "-" + date[6:8]
    
def hasT1(pth):
    files = os.listdir(pth)
    def t(x): return 'LAS' in x
    T1 = filter(t,files)
    return T1
    
def hasFLAIR(pth):
    files = os.listdir(pth)
    def f(x): return 'FLAIR' in x
    FLAIR = filter(f,files)
    return FLAIR
    
def hasRS(pth):
    files = os.listdir(pth)
    def f(x): return ('rsfMRI' in x) or ('Resting' in x)
    rs = filter(f,files)
    return rs
        
def getT1(pth, pair):
    os.chdir('/mnt/macdata/projects/images/' + getRange(pair[0]) + "/" + pair[0] + "/" + dateSL2Images(pair[1]))
    for f in os.listdir('.'): # cd to files
            if os.path.isdir(f):
                    os.chdir(f)
    try:
        os.system("cp MP-LAS*.* " + pth)
    except:
        log[str(pair[0])] += 'XT'
    else:
        log[str(pair[0])] += 'T'
        
def getFLAIR(pth, pair):
    os.chdir('/mnt/macdata/projects/images/' + getRange(pair[0]) + "/" + pair[0] + "/" + dateSL2Images(pair[1]))
    for f in os.listdir('.'): # cd to files
            if os.path.isdir(f):
                    os.chdir(f)
    try:
        os.system("cp FLAIR*.* " + pth)
    except:
        log[str(pair[0])] += 'XF'
    else:
        log[str(pair[0])] += 'F'
        
def getRS(pth, pair):
    os.chdir('/mnt/macdata/projects/images/' + getRange(pair[0]) + "/" + pair[0] + "/" + dateSL2Images(pair[1]))
    for f in os.listdir('.'): # cd to files
            if os.path.isdir(f):
                    os.chdir(f)
    try:
        os.system("cp rsfMRI*.zip " + pth)
    except:
        log[str(pair[0])] += 'XR'
    else:    
        log[str(pair[0])] += 'R'
        
def getRange(PIDN):
    PIDN = int(PIDN)
    if PIDN<1000:
        return "0000-0999"
    else:
        low = int(math.floor(PIDN/1000.0)) * 1000
        return str(low) + "-" + str(low+999)
        

# input plain text (space delimited), convert to list of PIDN-date pairs
f = open("images_to_add.txt")
data = f.readlines()
numImages = len(data)
images = []

log = dict() # list of pairs (+ what) added to SL drive; save it with the day's date at end.

for d in data:
    line = d.split()
    images.append(line)
    log[str(line[0])] = str(line[1])
    
# search seeley server for images & copy over

for pair in images:
    pth = "/data6/controlNIC/" + pair[0]
    if not os.path.exists(pth): # if no data for subject
        os.mkdir(pth) # add subject to SL
    if not os.path.exists(pth + "/" + pair[0] + "_" + pair[1] + "/"): # if no scan at this date in SL
        os.mkdir(pth + "/" + pair[0] + "_" + pair[1] + "/") # add to subj's SL folder
    # HANDLE RS    
    if not os.path.exists(pth + "/" + pair[0] + "_" + pair[1] + "/raw/"): # if no RS folder for scan at this date
        os.mkdir(pth + "/" + pair[0] + "_" + pair[1] + "/raw/") # add raw data folder
    if not hasRS(pth + "/" + pair[0] + "_" + pair[1] + "/raw/"): # has a raw folder, but no RS in the folder
        getRS(pth + "/" + pair[0] + "_" + pair[1] + "/raw/", pair) # copy resting state to raw folder
        # unzip it
        os.chdir(pth + "/" + pair[0] + "_" + pair[1] + "/raw/")
        os.system("unzip *vS2*.zip")
        os.system("unzip *vH1*.zip")
        for f in os.listdir('.'): # cd to files
                if os.path.isdir(f):
                        os.chdir(f)
        # convert dcm2nii; can check for .dcm v .IMA, .-
        os.system("dcm2nii -c n -d n -e n -f n -g n -i n -p y -n y -r n *.dcm")
        os.system("fslsplit *.nii")
        os.system("gunzip *.gz")
        os.system("mkdir ../../rsfmri")
        os.system("mkdir ../../rsfmri/nii")
        os.system("cp vol*.nii ../../rsfmri/nii")
        
    # HANDLE STRUC    
    if not os.path.exists(pth + "/" + pair[0] + "_" + pair[1] + "/struc/"):
        os.mkdir(pth + "/" + pair[0] + "_" + pair[1] + "/struc/")
    # T1
    if not hasT1(pth + "/" + pair[0] + "_" + pair[1] + "/struc/"):
        getT1(pth + "/" + pair[0] + "_" + pair[1] + "/struc/", pair) # copy T1 over from Images
    # FLAIR
    if not hasFLAIR(pth + "/" + pair[0] + "_" + pair[1] + "/struc/"):
        getFLAIR(pth + "/" + pair[0] + "_" + pair[1] + "/struc/", pair) # copy FLAIR over from Images
        
        
        
        
        
        
        # check for rsfmri(_new/rsfmri_closed) folder, nii folder -- make if necessary. move .niis
        #if os.path.exists(pth + "/" + pair[0] + "_" + pair[1] + "/rsfmri_new"):
        #    if os.path.exists(pth _ "/" + pair[0] + "_" + pair[1] + "rsfmri_new/nii")
        
        
     #save log
w = csv.writer(open("/data/mridata/akhazenzon/scripts/getImages/ImageImport_" + time + ".csv", "w"))
for key, val in log.items():
    w.writerow([key, val])


        
        
        
#importT1.m = Andrew's version of this

