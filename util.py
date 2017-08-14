import os
from multiprocessing import Pool
from subprocess import call
import json
from multiprocessing import Pool

IMAGE_TAR_NAME = "_tmp_image.tar"

def genLayer(name, path):
    return {"name": name, "path": path}

def genImage(name, layers):
    return {"name": name, "layers": layers}

def dockerPull(imageName):
    return call(["docker", "pull", imageName]) == 0

def dockerSave(imageName, imagePath):
    return call(["docker", "save", "-o", imagePath, imageName]) == 0

def extractImage(imagePath, imageFolder):
    return call(["tar", "-xf", imagePath, "-C", imageFolder])

def genImageFolder(imageName):
    # get the folder containing the extracted image
    # the sub file system should contain all saved and extracted image
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), "buffer", imageName.replace('/', ':'))

def getImageDigests(imageName):
    fs = genImageFolder(imageName)
    with open(os.path.join(fs, "manifest.json")) as f:
        d = json.load(f)[0]
        layers = []
        with open(os.path.join(fs, d["Config"])) as cfgF:
            cfgD = json.load(cfgF)
            for i, sha in enumerate(cfgD['rootfs']['diff_ids']):
                s = sha.split(":")
                if len(s) != 2:
                    s = s[0]
                layers.append(genLayer(s[1], os.path.join(fs, d['Layers'][i])))
        s = cfgD['config']['Image'].split(":")
        if len(s) != 2:
            s = s[0]
        return genImage(s[1], layers)

def pullImage(imageName):
    '''
    parseImage parses a image config.json file and get the digests of the image
    and all layers.
    '''
    imageFolder = genImageFolder(imageName)
    # absolute path to the buffered image
    imagePath = os.path.join(imageFolder, IMAGE_TAR_NAME)
    # only if the image tarball doesn't exist in the buffer, we pull down the image.
    if not os.path.isfile(imagePath):
        if call(["mkdir", "-p", imageFolder]) == 0:
            # try to save the image, if not successful, pull the image
            if not dockerSave(imageName, imagePath):
                if not (dockerPull(imageName) == 0 and dockerSave(imageName, imagePath) == 0):
                    print json.dumps({"error": "can't save the image."})
                    return False
            # extract the image into the folder
            extractImage(imagePath, imageFolder)
        return False
    return True

def pullImages(imageNames):
    print json.dumps({"event": "pulling %d images"%(len(imageNames, ))})
    uniqueNames = {}
    for i, name in enumerate(imageNames):
        uniqueNames[name] = i

    rc = {}
    p = Pool(len(uniqueNames))
    p.map(pullImage, uniqueNames.keys())