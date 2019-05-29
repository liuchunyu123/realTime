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

from tqdm import tqdm

cur_Intents_String = ""
class controller:
    def __init__(self):
        self.intentTree = verbalGraphGenerator.generate()


    def pick_path(self):
        node = self.intentTree.root
        path = []
        while node.getIntent() != verbalGraphGenerator.end:
            path.append(node)
            # print(node.getIntent())
            # node.showClds()
            # print(node.getIntent())
            if len(node.clds)<=0:
                break
            node_pre = node
            node = random.choice(node.clds)
            while node.getIntent()=="WFSB":
                node = random.choice(node_pre.clds)
        print_path = " --> ".join([item.getIntent() for item in path])
        print_verbal = " --> ".join([item.getVerbal() for item in path])
        logging.info("Randomly pick a routine:{print_path}".format(print_path=print_path))
        logging.info("verbal path:{print_verbal}".format(print_verbal = print_verbal))
        return path

    def regualr_routine(self,callId,path):
        path1 = path[:-1]
        path2 = path[1:]
        lastNode = None
        actual_path = []
        arriveEnd = True
        allRight = True

        right_len = 0
        for cur_node, next_node in zip(path1, path2):
            actual_path.append(cur_node)
            next_intent = self.oneAction(cur_node, next_node, callId)
            next_intentId = self.intentTree.intentAbbr2Id[next_intent]
            lastNode = next_node
            if next_intent != next_node.getIntent():
                logging.debug("Wrong!")
                allRight = False
                if next_intentId in cur_node.cldsIntentIdSet:
                    logging.debug("Begain select path by return intent!")
                else:
                    pot_intent = ",".join(item.getIntent() for item in cur_node.clds)
                    logging.debug("Return Intent {ret_intent} not in potential intent {pot_intent}".format(
                        ret_intent=next_intent, pot_intent=pot_intent))
                    arriveEnd = False
                    lastNode = None
                break

        return arriveEnd,allRight,lastNode,cur_node,next_intentId,actual_path,right_len

    def wrong_routine(self):
        pass

    def record_right_intent(self,total_dict,right_dict,node):
        t_dict = total_dict
        r_dict = right_dict
        name = node.getIntent()
        right_count = r_dict.get(name, 0)+1
        total_count = t_dict.get(name, 0)+1
        t_dict[name] = total_count
        r_dict[name] = right_count
        return t_dict,r_dict

    def record_wrong_intent(self,total_dict,node,sen,next_intent,intent_intent_sen_list):
        l = intent_intent_sen_list
        t_dict = total_dict
        name = node.getIntent()
        total_count = t_dict.get(name, 0) + 1
        t_dict[name] = total_count
        l.append([name,cur_Intents_String,sen.encode("utf-8")])
        return t_dict,l

    def record_time(self,time_list,t):
        time_list.append(t)
        return time_list




    def new_do(self):
        callId = str(uuid.uuid1())
        logging.info(callId)
        path = self.pick_path()
        init_len = len(path) - 1
        arriveEnd, allRight, lastNode, cur_node, next_intentId, actual_path, right_len = self.regualr_routine(callId,path)

        if not allRight and arriveEnd:
            return self.wrong_routine(actual_path,cur_node,next_intentId)

        print_actual_path = " --> ".join([item.getIntent() for item in actual_path])
        print_init_select_path = " --> ".join([item.getIntent() for item in path])

        return init_len,right_len,print_init_select_path,print_actual_path,arriveEnd,allRight

    def do(self,path):
        # pdb.set_trace()
        callId = str(uuid.uuid1())

        logging.info(callId)
        path1 = path[:-1]
        path2 = path[1:]
        lastNode =None
        actual_path = []
        arriveEnd = True
        allRight = True
        init_len = len(path)-1
        right_len = 0
        node_right_statistic = dict()
        node_total_statistic = dict()
        time_statistic = list()
        time_text = list()
        time_huashu = list()
        intent_intent_sen_list = list()
        for cur_node,next_node in zip(path1,path2):
            actual_path.append(cur_node)

            next_intent,pick_sen, textTime, huashuTime, totalTime = self.oneAction(cur_node,next_node,callId)

            self.record_time(time_statistic,totalTime)
            self.record_time(time_text,textTime)
            self.record_time(time_huashu,huashuTime)
            next_intentId = self.intentTree.intentAbbr2Id[next_intent]
            lastNode = next_node
            if next_intent!=next_node.getIntent():
                logging.debug("Wrong!")
                allRight = False
                node_total_statistic,intent_intent_sen_list = self.record_wrong_intent(node_total_statistic,next_node,pick_sen,next_intent,intent_intent_sen_list) #record
                if next_intentId in cur_node.cldsIntentIdSet:
                    logging.debug("Begain select path by return intent!")
                else:
                    pot_intent = ",".join(item.getIntent() for item in cur_node.clds)
                    logging.debug("Return Intent {ret_intent} not in potential intent {pot_intent}".format(
                        ret_intent=next_intent,pot_intent=pot_intent))
                    arriveEnd = False
                    lastNode = None
                    break

                while next_intentId in cur_node.cldsIntentIdSet:
                    cur_node = cur_node.intentId2item[next_intentId]
                    actual_path.append(cur_node)
                    if len(cur_node.clds)<=0:
                        lastNode = cur_node
                    else:
                        next_node = random.choice(cur_node.clds)
                        while next_node.getIntent() == "WFSB":
                            next_node = random.choice(cur_node.clds)
                        logging.info("change next node to ==>"+next_node.getIntent())
                        if next_node.getIntent() == verbalGraphGenerator.end:
                            lastNode = None
                            break

                        next_intent,pick_sen,textTime,huashuTime,totalTime = self.oneAction(cur_node, next_node,callId)

                        self.record_time(time_statistic, totalTime)
                        self.record_time(time_text, textTime)
                        self.record_time(time_huashu, huashuTime)
                        if next_intent == next_node.getIntent():  #record
                            node_total_statistic, node_right_statistic = self.record_right_intent(node_total_statistic,
                                                                                      node_right_statistic, next_node)
                        else:
                            node_total_statistic,intent_intent_sen_list = self.record_wrong_intent(node_total_statistic,next_node,pick_sen,next_intent,intent_intent_sen_list)

                        next_intentId = self.intentTree.intentAbbr2Id[next_intent]
                        if next_intentId not in cur_node.cldsIntentIdSet:
                            pot_intent = ",".join(item.getIntent() for item in cur_node.clds)
                            logging.debug("Return Intent {ret_intent} not in potential intent {pot_intent}".format(
                                ret_intent=next_intent, pot_intent=pot_intent))
                            arriveEnd = False
                            lastNode = None
                            break
                break
            right_len = right_len + 1
            node_total_statistic, node_right_statistic = self.record_right_intent(node_total_statistic,node_right_statistic,next_node)#record
        if lastNode:
            actual_path.append(lastNode)
            self.oneAction(lastNode,callId=callId)
        print_actual_path = " --> ".join([item.getIntent() for item in actual_path])
        print_init_select_path = " --> ".join([item.getIntent() for item in path])
        logging.info("Initial Intent Path: "+print_init_select_path)
        logging.info("Actual Intent Path: "+print_actual_path)
        if allRight:
            logging.info("Reach the end of the path!")
        if not arriveEnd:
            logging.info("Not arrived to end! ")

        ret_dict=dict()
        ret_dict["init_len"]=init_len
        ret_dict["right_len"]=right_len
        ret_dict["print_init_select_path"]=print_init_select_path
        ret_dict["print_actual_path"]=print_actual_path
        ret_dict["arriveEnd"] = arriveEnd
        ret_dict["allRight"]=allRight
        ret_dict["node_total_statistic"] = node_total_statistic
        ret_dict["node_right_statistic"]=node_right_statistic
        ret_dict["time_statistic"]=time_statistic
        ret_dict["time_text"]=time_text
        ret_dict["time_huashu"]=time_huashu
        ret_dict["intent_intent_sen_list"]=intent_intent_sen_list
        return ret_dict
        # return init_len,right_len,print_init_select_path,print_actual_path,arriveEnd,allRight,node_total_statistic,node_right_statistic,time_statistic,intent_intent_sen_list



    def sendSentence(self,sentence,callId,real=constants.EMULATOR):
        if real:
            return self.sendSentence_true(sentence,callId)
        else:
            return self.sendSentence_false(sentence,callId)

    def sendSentence_false(self,sentence,callId):
        logging.debug("Sending sendSentence:" + sentence)
        global cur_Intents_String
        sentence = "".join(sentence.split())
        origin_ret_intent, textTime = utils.uplaodText(sentence, callId)
        cur_Intents_String = origin_ret_intent
        splited_ret_intent = origin_ret_intent.split('/')
        ret_intent = splited_ret_intent[0]
        if ret_intent not in self.intentTree.intentAbbr2Id.keys():
            ret_intent = verbalGraphGenerator.end
            logging.error("NLU return a None Exist Intent! END instead!")
        return ret_intent, textTime

    def sendSentence_true(self,sentence,callId):
        callId = "defaultCallId"
        raw_input("Say:{sentence}\n Type <enter>".format(sentence=sentence.encode('utf-8')))
        logging.info("Waiting NLU recognize result:")
        start = time.time()
        with tqdm(total=100) as pbar:
            while not utils.haveRecogResult():
                time.sleep(0.05)
                pbar.update(5)
                end = time.time()
                # if end-start>10:
                #     return verbalGraphGenerator.end,end-start

        intent = utils.getNLUIntent()
        intent= intent.split("#")
        text = intent[-1]
        intent = intent[0]
        print("NLU Intent:"+intent.encode('utf-8'))
        print("NLU text:"+text.encode('utf-8'))
        end = time.time()
        return intent,start-end

    def sendTTS(self,node,callId):
        # tts = "_".join(node.getPreVerbal())
        tts = node.getVerbal()
        logging.debug("Sending TTS:"+tts)
        if constants.EMULATOR:
            utils.cleanIntentResult()
        textTime=utils.uploadHuaShu(tts,callId)
        return textTime




    def pickSentence(self,node):
        catName = node.getIntent()
        logging.debug("In pickSentence")
        ret_sen = utils.select_text(catName)
        return ret_sen

    def oneAction(self,cur_node,next_node=None,callId="1"):
        huashuTime=self.sendTTS(cur_node,callId)
        sen = ""
        if next_node:
            sen = self.pickSentence(next_node)
            ret_intent,textTime = self.sendSentence(sen,callId)
            totalTime=round((float(huashuTime)+float(textTime)),6)
            return ret_intent,sen,textTime,huashuTime,totalTime
        else:
            ret_intent = verbalGraphGenerator.end
        return ret_intent,sen

    def gen_paths(self,num):
        pikced_paths = []
        for _ in range(num):
            pikced_paths.append(self.pick_path())
        return pikced_paths
def main(iterNum):
    clt = controller()
    endCount = 0
    rightCount = 0
    total_right_length = 0
    total_init_length = 0
    save_file_Name = constants.HIST_DIR + os.sep +utils.getTimeStamp()
    save_sen_Name = save_file_Name+"_wrong_intent_sen"
    logging.info("Saving summary in===>"+save_file_Name)
    max_time_consuming = 0
    min_time_consuming = 1000000
    average_time_consuming = 0
    step_statistic_dict=dict()
    node_total_statistic_dict=dict()
    node_right_statistic_dict=dict()
    verbal_total_statistic_dict = dict()
    verbal_right_statistic_dict = dict()
    node_right_prob_dict = dict()
    intent_intent_sen_list = list()
    tmp_sum_time = 0
    tmp_avg_time = 0
    tmp_max_time = 0
    tmp_min_time = 0
    picked_paths = clt.gen_paths(iterNum)


    with codecs.open(save_file_Name,"w","utf-8") as f:
        for i,path in enumerate(picked_paths):
            if constants.EMULATOR:
                utils.resetNlu()
            f.write("#========{num}=========#\n".format(num = str(i)))
            logging.info("#========{num}=========#\n".format(num = str(i)))
            # init_len,right_len,s_path,a_path,end,right,node_total_statistic,node_right_statistic,time_statistic,tmp_intent_intent_sen_list  = clt.do(path)
            ret_dict = clt.do(path)
            init_len = ret_dict["init_len"]
            right_len = ret_dict["right_len"]
            s_path = ret_dict["print_init_select_path"]
            a_path = ret_dict["print_actual_path"]
            end = ret_dict["arriveEnd"]
            right = ret_dict["allRight"]
            node_total_statistic = ret_dict["node_total_statistic"]
            node_right_statistic = ret_dict["node_right_statistic"]
            time_statistic = ret_dict["time_statistic"]
            time_huashu = ret_dict["time_huashu"]
            time_text = ret_dict["time_text"]
            tmp_intent_intent_sen_list = ret_dict["intent_intent_sen_list"]

            intent_intent_sen_list = intent_intent_sen_list+tmp_intent_intent_sen_list

            total_init_length = total_init_length+init_len
            total_right_length = total_right_length+right_len
            f.write("initPath:{path}\n".format(path = s_path))
            f.write("actualPath:{path}\n".format(path = a_path))
            f.write("init length {len1},right length {len2},rate:{rate}\n".format(
                len1=init_len,len2=right_len,rate=float(right_len)/init_len))
            step_statistic_dict[right_len] = step_statistic_dict.get(right_len,0)+1
            max_time_consuming = max(max_time_consuming,max(time_statistic))
            min_time_consuming = min(min_time_consuming,min(time_statistic))
            tmp_sum_time = sum(time_statistic)
            tmp_avg_time = tmp_sum_time/len(time_statistic)
            tmp_max_time = max(time_statistic)
            tmp_min_time = min(time_statistic)
            f.write("Time consuming:\n")
            f.write("upload_huashu : {time}\n".format(time=time_huashu))
            f.write("upload_text : {time}\n".format(time=time_text))
            f.write("upload_time : {time}\n".format(time=time_statistic))
            f.write("max : {time}\n".format(time=tmp_max_time))
            f.write("min :{time}\n".format(time=tmp_min_time))
            f.write("avg :{time}\n".format(time=tmp_avg_time))
            f.write("Total :{time}\n".format(time=tmp_sum_time))
            average_time_consuming = average_time_consuming+sum(time_statistic)
            for k,v in node_right_statistic.items():
                node_right_statistic_dict[k] = node_right_statistic_dict.get(k,0)+1

            for k,v in node_total_statistic.items():
                node_total_statistic_dict[k] = node_total_statistic_dict.get(k,0)+1


            if right:
                rightCount = rightCount+1
                f.write("Right?:True\n")
            else:
                f.write("Right?:False\n")
            if end:
                endCount = endCount+1
                f.write("Finish?:True\n")
            else:
                f.write("Finish?:False\n\n")

        f.write("SUMMARIZE:\n")
        f.write("\titerat {iterNum} nums\n".format(iterNum = iterNum))
        f.write("\tComplete right:{rightCount}, prob:{prob}\n".format(rightCount=rightCount,prob = float(rightCount)/iterNum))
        f.write("\tFinish :{endCount}, prob:{prob}\n".format(endCount = endCount,prob = float(endCount)/iterNum))
        f.write("\tright/init length rate:{rate}\n".format(rate = float(total_right_length)/total_init_length))


        total_intent = sum([v for k,v in node_total_statistic_dict.items()])
        f.write("\tTIME CONSUMING:\n")
        f.write("\t\tmax : {time}\n".format(time=max_time_consuming))
        f.write("\t\tmin :{time}\n".format(time=min_time_consuming))
        f.write("\t\tavg :{time}\n".format(time=average_time_consuming/total_intent))
        f.write("\t\tTotal :{time}\n".format(time=average_time_consuming))

        for k in node_total_statistic_dict.keys():
            if k not in node_right_statistic_dict.keys():
                node_right_prob_dict[k] = 0
            else:
                node_right_prob_dict[k] = float(node_right_statistic_dict[k])/node_total_statistic_dict[k]

        step_statistic_list = sorted(step_statistic_dict.items(), key=lambda x: x[1])
        # node_total_statistic_list = sorted(node_total_statistic_dict.items(), key=lambda x: x[1])
        # node_right_statistic_list = sorted(node_total_statistic_dict.items(), key=lambda x: x[1])
        node_right_prob_list = sorted(node_right_prob_dict.items(), key=lambda x: x[1])




        f.write("\tSTEP-NUM:\n")
        for item in step_statistic_list:
            f.write("\t\t{step} - {num}\n".format(step=item[0],num=item[1]))


        f.write("\tINTENT - PROB , (right/total):\n")

        sum_prob = 0
        for index,item in enumerate(node_right_prob_list):
            f.write("\t\t{node} - {prob} , ({right}/{total})\n".format(node=item[0],
                                                                   prob=item[1],
                                                                   right=node_right_statistic_dict.get(item[0],0),
                                                                   total=node_total_statistic_dict[item[0]]))
            sum_prob = sum_prob+float(item[1])
        avg_prob = sum_prob/(index+1)
        f.write("avg precision: "+str(avg_prob)+"\n")

    with open(save_sen_Name,'w') as f:
        for item in intent_intent_sen_list:
            f.write("{intent1} - {intent2}\n".format(intent1=item[0],intent2=item[1]))
            f.write("\t{sen}".format(sen=item[2]))










if __name__ == "__main__":
    logger.setup_logging()
    parser = argparse.ArgumentParser()
    parser.add_argument("--iterNum",'-i',default=10,help = "iteration num!")
    parser.add_argument("--randomSeed",'-rs',default=None,help = "random seed!")
    args = parser.parse_args()
    constants.RANDOM_SEED = args.randomSeed
    if constants.RANDOM_SEED:
        random.seed(constants.RANDOM_SEED)
    main(int(args.iterNum))

