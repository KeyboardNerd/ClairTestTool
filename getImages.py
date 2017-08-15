import requests
import sys
import os
import json
import time
from multiprocessing import Pool
import util
import api

if __name__ == "__main__":
    clairVersion = int(sys.argv[1])
    images = sys.argv[2:]
    util.pullImages(images)
    # concurrently gets image from Clair.
    p = Pool(len(images))
    if clairVersion == 1:
        p.map(api.mapGetImageV1, images)
    elif clairVersion == 2:
        p.map(api.mapGetImageV2, images)
    elif clairVersion == 3:
        p.map(api.mapGetImageV3, images)
    else:
        exit(-1)
