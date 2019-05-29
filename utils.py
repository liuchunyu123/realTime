#coding=utf-8
import  requests
import sys
sys.path.append("../")
from src import constants
from src import interface
import time
import json
import  logging
import os
import random
import codecs
import requests

def uploadHuaShu(text,callId):
    body = interface.huaShu()
    body.text = text
    body.callID = callId
    body.timestamp = getTimeStamp()
    jsonc = json.dumps(body.getDict())
    logging.info("upload data: "+jsonc)
    # start = time.time()
    r = requests.post(constants.HUSHU_UPLOAD_URL,jsonc)
    # end = time.time()
    huashuTime=round(float(r.elapsed.microseconds)/1000000,6)
    logging.info("upload HuaShu Time: "+ str(huashuTime))
    logging.info("upload HuaShu "+body.text)
    if r.json()['status'] != "Success":
        logging.error("upload Hua Shu Failed")
    return huashuTime


def uplaodText(text,callId):
    body = interface.textUploader()
    body.callId = callId
    body.text = text
    jsonc = json.dumps(body.getDict())
    logging.info("upload text " + body.text)
    # start = time.time()
    logging.info("upload data: "+jsonc)
    r = requests.post(constants.SENTENCE_UPLOAD_URL,jsonc)
    TextTime=round(float(r.elapsed.microseconds)/1000000,6)
    logging.info("upload text Time: " + str(TextTime))

    # end = time.time()
    # if r.json()['status'] != "Success":
    #     logging.error("upload Hua Shu Failed")
    #     return "END"
    # else:
    ret_intent = r.json().get("intent_cat", "END")
    logging.info("NLU return intent :"+ret_intent)
    return ret_intent,TextTime




def getTimeStamp():
    now = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))
    return now
cache_text = {}
def select_text(catName):
    dataDir = constants.SELECT_DATA_DIR.format(catName = catName)
    logging.info("dataDir:"+dataDir)
    if dataDir not in cache_text.keys():
        with codecs.open(dataDir,'r','utf-8') as f:
            content = f.readlines() 
        texts=[]
        tmp_text = []
        for c in content:
            if c.startswith("#") or c.startswith("---#"):
                if len(tmp_text)>0:
                    texts.append("".join(tmp_text))
                    tmp_text = []
            else:
                tmp_text.append(c)
        if len(tmp_text)>0:
            texts.append("".join(tmp_text))
        cache_text[dataDir]=texts


    texts = cache_text[dataDir]
    assert  len(texts)>=1
    content = random.choice(texts)
    logging.info("+++ catName: " + catName+" ++++ select from : "+dataDir)
    return content

def haveRecogResult():
    ret = requests.get(constants.DATA_RECEIVE_URL+"/haveData")
    return ret.text

def getNLUIntent():
    ret = requests.get(constants.DATA_RECEIVE_URL + "/getIntent")
    return ret.text.strip()

def cleanIntentResult():
    requests.get(constants.DATA_RECEIVE_URL+"/cleanIntent")

def resetNlu():
    param = {"callId":"defaultCallId"}
    requests.get(constants.RESET_URL,params=param)

if __name__ == "__main__":
    # uploadHuaShu("MZ125","1")
    # print (uplaodText("不是我","1"))
    print(haveRecogResult())
    print(getNLUIntent())
