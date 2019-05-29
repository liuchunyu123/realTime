#coding=utf-8
import sys
sys.path.append("../")
from src import verbalGraphGenerator
import random
from src import  logger
import logging
import uuid
from src import utils
from src import  constants
import argparse
import codecs
import os
import time
import pdb
import json
import threading





sentences=dict()
verbal_dict = dict()
cache_clds=dict()
intent_statistic=dict()
count=[0]

ret_dict = dict()
wrong_intent_statistic = dict()

total_key = "total"
true_key = "right"





def construct_verbal_dict(node,huashu_path):
    if node.getIntent() == verbalGraphGenerator.start:
        next_huashu_path=[]
        next_huashu_path.append(node.getVerbal())
    elif node.getIntent() == "WFSB":
        next_huashu_path = huashu_path[:]
        next_huashu_path.extend([node.getIntent(), node.getVerbal()])
    else:
        huashu_key = "_".join(huashu_path)
        intent_key = node.getIntent().strip()
        verbal_dict.setdefault(huashu_key,[]).append(intent_key)
        next_huashu_path = huashu_path[:]
        next_huashu_path.extend([node.getIntent(), node.getVerbal()])

    for cld in node.clds:
        if cld.getIntent().strip() != verbalGraphGenerator.end:
            construct_verbal_dict(cld,next_huashu_path)

    jsonDump(verbal_dict,"verbalDict")

def jsonDump(save_dict,fileName,myindent=4):
    fileName = constants.HIST_DIR + os.sep + utils.getTimeStamp()+"_"+fileName
    f = codecs.open(fileName,"w",'utf-8')
    json.dump(save_dict,f,indent=myindent)


def multiThreadVisit(pool_size=10):
    threads = []
    for huashu_key,intent_list in verbal_dict.items():
        threads.append(threading.Thread(target= actualVisit,args=(huashu_key,intent_list)))

    count =0
    need_join = []
    for t in threads:
        t.start()
        need_join.append(t)
        count+=1
        if count%pool_size ==0:
            logging.info(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"+str(count))
            for item in need_join:
                item.join()
            need_join=[]

    summaryNew()



def actualVisit(huashu_key,intent_list):
    same_level_intents = "_".join(intent_list)
    for cur_intent in intent_list:
        visitIntent(cur_intent,same_level_intents,huashu_key)
    visitOther(same_level_intents,huashu_key,intent_list)



def visitIntent(intent,same_level_intents,huashu_key):
    cache_dict = cache_clds.get(same_level_intents, {})
    if intent not in cache_dict.keys():
        cache_action(cache_dict, same_level_intents, intent, intent, huashu_key, total_key,
                     true_key, pre_ret_intent=intent)
    else:
        logging.info("In cache.....{same_level_intents}/{intent}".format(same_level_intents=same_level_intents,
                                                                         intent=intent))
    addFromCache(ret_dict, cache_clds, huashu_key, intent, same_level_intents, total_key, true_key)


def visitOther(same_level_intents,huashu_key,intent_list):
    intent_key = "other_intent"
    cache_dict = cache_clds.get(same_level_intents, {})
    if intent_key not in cache_dict.keys():
        for cur_intent in verbalGraphGenerator.intentId2Abbre:
            cur_intent = cur_intent.strip()
            if cur_intent not in intent_list and cur_intent != verbalGraphGenerator.start and cur_intent != verbalGraphGenerator.end and cur_intent != "WFSB":
                cache_action(cache_dict, same_level_intents, intent_key, cur_intent, huashu_key,
                             total_key, true_key, pre_ret_intent="WFSB")
    else:
        logging.info("In cache.....{same_level_intents}/{intent}".format(same_level_intents=same_level_intents,
                                                                         intent=intent_key))
    addFromCache(ret_dict, cache_clds, huashu_key, intent_key, same_level_intents, total_key, true_key)


def summaryNew():
    new_dict = {}
    for k, v in ret_dict.items():
        total = 0
        right = 0
        for inner_k, inner_v in v.items():
            total += inner_v["total"]
            right += inner_v['right']
        new_dict[k] = {"prob": float(right) / total, "right": right, "total": total}

    jsonDump(intent_statistic,"regular_intent_prob")
    jsonDump(ret_dict,"regular_detail")
    jsonDump(new_dict,"regular_brief")
    jsonDump(wrong_intent_statistic,"wrong_intent_sen_json")
    save_wrong_intent()

def save_regualr_intent_prob():
    fileName = constants.HIST_DIR + os.sep + utils.getTimeStamp() + "_" + "regular_intent_prob"
    with codecs.open(fileName,'w','utf-8') as f:
        sum_prob = 0
        count = 0
        for intent,static in intent_statistic.items():
            f.write("\t\t{node} - {prob} , ({right}/{total})\n".format(node=intent,
                                                                       prob=static['prob'],
                                                                       right=static['right'],
                                                                       total=static['total']))
            count +=1
            sum_prob += float(static['prob'])
        avg_prob = sum_prob / (count+ 1)
        f.write("avg precision: " + str(avg_prob) + "\n")




def save_wrong_intent():
    fileName = constants.HIST_DIR + os.sep + utils.getTimeStamp() + "_" + "wrong_intent_sen"
    with codecs.open(fileName,'w','utf-8') as f:
        for k,v in wrong_intent_statistic.items():
            for sentence in v:
                f.write(k+"\n")
                f.write("\t"+sentence+"\n")



def pre_visit(node,huashu_path,ret_dict,same_level_intents):
    """

    :param node: intentNode
    :param huashu_path:[mk01,mk02...,mk04]
    :param ret_dict:
                {
                话术路径1:
                {意图1:{right:10,total:30},
                意图2：{right:10,total:30}
                },
                话术路径2:
                {意图1:{right:10,total:30},
                意图2：{right:10,total:30}
                }
                ...
                ...
                }

    :return: ret_dict
    """
    logging.info("_".join(huashu_path))
    true_key = "right"
    total_key = "total"
    count[0] +=1
    logging.info("Intent node number: "+str(count[0]))

    if node.getIntent() == verbalGraphGenerator.start:
        next_huashu_path=[]
        next_huashu_path.append(node.getVerbal())
    elif node.getIntent() == "WFSB":
        next_huashu_path = huashu_path[:]
        next_huashu_path.extend([node.getIntent(), node.getVerbal()])

    else:
        huashu_key = "_".join(huashu_path)
        intent_key = node.getIntent().strip()
        cur_intent = intent_key
        cache_dict = cache_clds.get(same_level_intents, {})
        if intent_key not in cache_dict.keys():
            cache_action( cache_dict,same_level_intents, intent_key, cur_intent, huashu_key, total_key,
                     true_key, pre_ret_intent=cur_intent)
        else:
            logging.info("In cache.....{same_level_intents}/{intent}".format(same_level_intents=same_level_intents,
                                                                             intent=intent_key))


        addFromCache(ret_dict, cache_clds, huashu_key, intent_key, same_level_intents, total_key, true_key)


        next_huashu_path = huashu_path[:]
        next_huashu_path.extend([node.getIntent(),node.getVerbal()])



    clds = node.clds
    clds_intent = "_".join(sorted([item.getIntent().strip() for item in clds]))


    #walk
    for cld in clds:
        if   cld.getIntent().strip()==verbalGraphGenerator.end:
            continue
        logging.info("visit "+cld.getIntent())
        pre_visit(cld,next_huashu_path,ret_dict,clds_intent)

    if clds:
        huashu_key = "_".join(next_huashu_path)
        # huashu_key = "_".join(huashu_path)
        intent_key = "other_intent"
        clds_intents = set([item.getIntent().strip() for item in clds])
        same_level_intents = "_".join(sorted(list(clds_intents)))
        cache_dict = cache_clds.get(same_level_intents, {})
        if intent_key not in cache_dict.keys():
            for cur_intent in verbalGraphGenerator.intentId2Abbre:
                cur_intent = cur_intent.strip()
                if cur_intent not in clds_intents and cur_intent!=verbalGraphGenerator.start and cur_intent!=verbalGraphGenerator.end and cur_intent!="WFSB":
                    cache_action(cache_dict,same_level_intents, intent_key, cur_intent, huashu_key,
                                 total_key,true_key,  pre_ret_intent="WFSB")
        else:
            logging.info("In cache.....{same_level_intents}/{intent}".format(same_level_intents=same_level_intents,
                                                                             intent=intent_key))
        addFromCache(ret_dict,cache_clds,huashu_key,intent_key,same_level_intents,total_key,true_key)

    return ret_dict
    #do


def cache_action(cache_dict,same_level_intents,intent_key,cur_intent,huashu_key,total_key,true_key,pre_ret_intent="WFSB"):

    intent_sentences = sentences[cur_intent]
    tmp_intent_val = cache_dict.get(intent_key, {})

    for index, sen in enumerate(intent_sentences):

        call_id = str(uuid.uuid1())
        # move_to_position(huashu_path,call_id)
        utils.uploadHuaShu(huashu_key, call_id)
        origin_ret_intent, c_time = utils.uplaodText(sen, call_id)
        splited_ret_intent = origin_ret_intent.split('/')
        ret_intent = splited_ret_intent[0]
        intent_total_count = tmp_intent_val.get(total_key, 0) + 1
        tmp_intent_val[total_key] = intent_total_count
        if ret_intent == pre_ret_intent:
            intent_true_count = tmp_intent_val.get(true_key, 0) + 1
            tmp_intent_val[true_key] = intent_true_count
        else:
            wrong_key = " - ".join([huashu_key,pre_ret_intent,origin_ret_intent])
            wrong_intent_statistic.setdefault(wrong_key,[]).append(sen)
        cache_dict[intent_key] = tmp_intent_val
        cache_clds[same_level_intents] = cache_dict


        #统计意图
        if pre_ret_intent != "WFSB":

            intent_statistic_value = intent_statistic.get(pre_ret_intent,{})
            total = intent_statistic_value.get("total",0)+1
            right = intent_statistic_value.get("right", 0)
            intent_statistic_value["total"] = total
            if ret_intent == pre_ret_intent:
                right = right+1
                intent_statistic_value["right"] = right
            intent_statistic_value["right"] = right
            intent_statistic_value["prob"] = float(right)/total

            intent_statistic[pre_ret_intent] = intent_statistic_value






def addFromCache(ret_dict,cache_clds,huashu_key,intent_key,same_level_intents,total_key,true_key):
    huashu_val = ret_dict.get(huashu_key, {})
    intent_val = huashu_val.get(intent_key, {})
    cache_dict = cache_clds[same_level_intents]
    if intent_key not in cache_dict.keys():
        return
    cache_intent_val = cache_dict[intent_key]
    intent_total_count = intent_val.get(total_key, 0) + cache_intent_val.get(total_key, 0)
    intent_true_count = intent_val.get(true_key, 0) + cache_intent_val.get(true_key, 0)
    intent_val[true_key] = intent_true_count
    intent_val[total_key] = intent_total_count
    huashu_val[intent_key] = intent_val
    ret_dict[huashu_key] = huashu_val




def move_to_position(huashu_path,call_id):
    if len(huashu_path)==0:
        return
    elif len(huashu_path)==1:
        utils.uploadHuaShu(huashu_path[0], call_id)
        return

    for item in huashu_path[:-1]:
        utils.uploadHuaShu(item,call_id)
        utils.uplaodText("move to position!",call_id)
    utils.uploadHuaShu(huashu_path[-1], call_id)


def get_sentence(file_path):
    global sentences
    with codecs.open(file_path,'r',encoding="utf-8") as f:
        contents = f.readlines()
    for item in contents:
        item_splited = item.split('\t')
        sen = item_splited[0].strip()
        key = item_splited[1].strip()
        sen_list = sentences.get(key,[])
        sen_list.append(sen)
        sentences[key] = sen_list
    ret_sentences = sentences
    return ret_sentences


def summary(summary_dict):
    save_file_Name = constants.HIST_DIR + os.sep + utils.getTimeStamp()+"_regular_detail"
    save_file_Name_brief = constants.HIST_DIR + os.sep + utils.getTimeStamp()+"_regular_brief"
    save_file_Name_intent_prob = constants.HIST_DIR + os.sep + utils.getTimeStamp() + "_regular_intent_prob"
    f1 = codecs.open(save_file_Name,'w','utf-8')
    f2 = codecs.open(save_file_Name_brief,'w','utf-8')
    f3 = codecs.open(save_file_Name_intent_prob,'w','utf-8')
    new_dict = {}
    for k,v in summary_dict.items():
        total = 0
        right = 0
        for inner_k,inner_v in v.items():
            total += inner_v["total"]
            right += inner_v['right']
        new_dict[k] ={"prob": float(right)/total,"right":right,"total":total}

    json.dump(summary_dict, f1, indent=4)
    json.dump(new_dict, f2, indent=4)
    json.dump(intent_statistic, f3, indent=4)






if __name__ =="__main__":
    logger.setup_logging()
    tree = verbalGraphGenerator.verbalTree()
    get_sentence(file_path="../doc/output1")
    # ret_dict = pre_visit(tree.root,[],{},verbalGraphGenerator.start)
    # summary((ret_dict))
    construct_verbal_dict(tree.root,[])
    multiThreadVisit()





