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
        
def getT1(pth, pidn, date):
    os.chdir('/mnt/macdata/projects/images/' + getRange(pidn) + "/" + pidn + "/" + dateSL2Images(date))
    for f in os.listdir('.'): # cd to files
            if os.path.isdir(f):
                    os.chdir(f)
    try:
        os.system("cp MP-LAS*.* " + pth)
    except:
        log[str(pidn)] += 'XT'
    else:
        log[str(pidn)] += 'T'
        
def getFLAIR(pth, pidn, date):
    os.chdir('/mnt/macdata/projects/images/' + getRange(pidn) + "/" + pidn + "/" + dateSL2Images(date))
    for f in os.listdir('.'): # cd to files
            if os.path.isdir(f):
                    os.chdir(f)
    try:
        os.system("cp FLAIR*.* " + pth)
    except:
        log[str(pidn)] += 'XF'
    else:
        log[str(pidn)] += 'F'
        
def getRS(pth, pidn, date):
    os.chdir('/mnt/macdata/projects/images/' + getRange(pidn) + "/" + pidn + "/" + dateSL2Images(date))
    for f in os.listdir('.'): # cd to files
            if os.path.isdir(f):
                    os.chdir(f)
    try:
        os.system("cp rsfMRI*.zip " + pth)
    except:
        log[str(pidn)] += 'XR'
    else:    
        log[str(pidn)] += 'R'
        
def getRange(pidn):
    if int(pidn)<1000:
        return "0000-0999"
    else:
        low = int(math.floor(pidn/1000.0)) * 1000
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
    pidn, date = pair
    pth = "/data6/controlNIC/" + pidn
    if not os.path.exists(pth): # if no data for subject
        os.mkdir(pth) # add subject to SL
    pth += pidn + "/"
    if not os.path.exists(pth + pidn + "_" + date + "/"): # if no scan at this date in SL
        os.mkdir(pth + ) # add to subj's SL folder
    pth += pidn + "_" + date + "/"    
    
    f = os.listdir('.')
    rs_dir = filter(lambda x: not('._' in x) and ('images' in x), f)
    
    #os.path.exists(pth + "rsfmri_new/nii/")
    #os.path.exists(pth + "rsfmri_new/rsfmri_closed/nii/")
    
    # HANDLE RS
    if not os.path.exists(pth + "raw/"): # if no RS folder for scan at this date
        os.mkdir(pth + "raw/") # add raw data folder
    if not hasRS(pth + "raw/"): # has a raw folder, but no RS in the folder
        getRS(pth + "raw/", pidn, date) # copy resting state to raw folder
        # unzip it
        os.chdir(pth + "raw/")
        if os.system("ls | grep .zip") == 0:
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
        
    # /struc
    if not os.path.exists(pth "struc/"):
        os.mkdir(pth + "struc/")
    # T1
    if not hasT1(pth + "struc/"):
        getT1(pth + "struc/", pidn, date) # copy T1 over from Images
    # FLAIR
    if not hasFLAIR(pth + "struc/"):
        getFLAIR(pth + "struc/", pidn, date) # copy FLAIR over from Images
        
        # check for rsfmri(_new/rsfmri_closed) folder, nii folder -- make if necessary. move .niis
        #if os.path.exists(pth + "/" + pidn + "_" + date + "/rsfmri_new"):
        #    if os.path.exists(pth _ "/" + pidn + "_" + date + "rsfmri_new/nii")
        
        # eventually add a check for already preprocessed files
        
     #save log
w = csv.writer(open("/data/mridata/akhazenzon/scripts/getImages/ImageImport_" + time + ".csv", "w"))
for key, val in log.items():
    w.writerow([key, val])


        
        
        
#importT1.m = Andrew's version of this

