import api
import util
import sys
from multiprocessing import Pool

SEQ = False
if __name__ == '__main__':
    clairVersion = int(sys.argv[1])
    images = sys.argv[2:]
    util.pullImages(images)
    if not SEQ:
        p = Pool(len(images))
        if clairVersion == 1:
            p.map(api.mapPostImageV1, images)
        elif clairVersion == 2:
            p.map(api.mapPostImageV2, images)
        elif clairVersion == 3:
            p.map(api.mapPostImageV3, images)
        else:
            exit(-1)
    else:
        if clairVersion == 1:
            map(api.mapPostImageV1, images)
        elif clairVersion == 2:
            map(api.mapPostImageV2, images)
        elif clairVersion == 3:
            map(api.mapPostImageV3, images)
        else:
            exit(-1)
