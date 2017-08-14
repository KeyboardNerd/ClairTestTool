import json
import sys
import os
import requests
from multiprocessing import Pool
from subprocess import call
import time
import util
import uuid

V3HOST = 'http://127.0.0.1:6080'
V2HOST = 'http://127.0.0.1:6060'
V1HOST = 'http://127.0.0.1:6070'
VERBOSE = True

def postImageV1(url, name):
    addr = url + '/v1/layers'
    # V1 api requires sequentially pushing layers to server, you can not process
    # layers concurrently.
    image = util.getImageDigests(name)
    imageName = image['name']
    total = 0
    failed = False
    for i, l in enumerate(image['layers']):
        parent = ""
        if i > 0:
            parent = genV1LayerName(image, i-1)
        postBody = {
            "Layer" : {
                "Name": genV1LayerName(image, i), # unique for each image
                "Path": l['path'],
                "ParentName": parent,
                "Format": "Docker"
            },
        }

        start = time.time()
        r = requests.post(addr, data=json.dumps(postBody))
        total += (time.time() - start)
        res = {
            "rc": r.status_code,
            "req": r.url,
            "res": r.json(),
        }
        if VERBOSE:
            print json.dumps(res)
        if r.status_code >= 400:
            failed = True
    print json.dumps({"success": not failed, "image": name, "time": total*1000})
    return total

def postImageV2(url, name):
    addr = url + '/ancestry'
    # v1 version of posting an image.
    image = util.getImageDigests(name)
    # generate the post request
    layers = []
    for l in image['layers']:
        layers.append({'hash': l['name'], 'path': l['path']})

    postBody = {
        "ancestry_name": image['name'],
        "format": "Docker",
        "layers": layers
    }

    start = time.time()
    r = requests.post(addr, data=json.dumps(postBody))
    t = time.time() - start
    res = {
        "image": name,
        "status": r.status_code,
        "time": (time.time() - start)*1000
    }
    if VERBOSE:
        res['res'] = r.json()
        res['url'] = r.url
        res['req'] = postBody
    print json.dumps(res)
    return t

def genV1LayerName(imageDef, layerINX):
    return imageDef['name'][:16] + imageDef['layers'][layerINX]['name'][:16]

def getImageV1(url, name):
    addr = url + '/v1/layers/'
    image = util.getImageDigests(name)
    layerName = genV1LayerName(image, -1)

    start = time.time()
    r = requests.get(addr+layerName+"?features&vulnerabilities")
    res = {
        "image": name,
        "success": r.status_code < 400,
        "time": (time.time() - start)*1000
    }
    if VERBOSE:
        res['req'] = r.url
        res['res'] = r.json()
    print json.dumps(res)

def getImageV2(url, name):
    addr = url + '/ancestry/'
    image = util.getImageDigests(name)
    start = time.time()
    r = requests.get(addr + image['name'], params={"with_vulnerabilities": True, "with_features": True})
    res = {
        "image": name,
        "success": r.status_code < 400,
        "time": (time.time() - start)*1000
    }
    if VERBOSE:
        res["req"] = r.url
        res["res"] = r.json()
    print json.dumps(res)

def mapPostImageV3(name):
    postImageV2(V3HOST, name)

def mapPostImageV1(name):
    postImageV1(V1HOST, name)

def mapPostImageV2(name):
    postImageV1(V2HOST, name)

def mapGetImageV1(name):
    getImageV1(V1HOST, name)

def mapGetImageV2(name):
    getImageV1(V2HOST, name)

def mapGetImageV3(name):
    getImageV2(V3HOST, name)
