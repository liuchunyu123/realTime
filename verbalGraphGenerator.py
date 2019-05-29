# -*- coding: UTF-8 -*-
import sys
sys.path.append("../")
import pandas as pd
import pdb
# import sys
import re
import logging
import json
# reload(sys)
# sys.setdefaultencoding('utf-8')


intentId2Abbre = list()
intentAbbr2Id = dict()
verbalId2Abbre = list()
verbalAbbre2Id = dict()

start = "START"
end = "END"

intentId2Abbre = [start]
intentAbbr2Id = dict({start:0})
verbalId2Abbre = list()
verbalAbbre2Id = dict()



class verbalTree:
    def __init__(self,xlsx=u"../doc/intent.xlsx"):
        self.xlsx = xlsx
        self.root = None
        logging.info("Bulding intent and verbal Tree ......")
        logging.info("Read content from xlsx......,(Path:{path})".format(path=self.xlsx))
        self.df = pd.read_excel(self.xlsx)
        self.remove_redundant()
        #     logging.info("Add start intent ......")
        self.addStartCol()
        self.buildTree(self.df)
        self.intentId2Abbre = intentId2Abbre
        self.intentAbbr2Id = intentAbbr2Id
        self.verbalId2Abbre = verbalId2Abbre
        self.verbalAbbre2Id = verbalAbbre2Id

    def buildTree(self,df, parent_node=None):
        # print(df.shape)
        # print(df.iloc[:][0])
        # node = None
        for rx in range(df.shape[0]):
            if df.iloc[rx,0]!=df.iloc[rx,0]:
                continue
            intent = df.iloc[rx][0]
            verbal = df.iloc[rx][1]
            tmp_rx = rx
            if verbal != verbal:

                while tmp_rx > 0 and verbal != verbal :
                    tmp_rx = tmp_rx - 1
                    verbal = df.iloc[tmp_rx,1]
            up_bound = tmp_rx
            while tmp_rx+1 < df.shape[0] and df.iloc[tmp_rx+1 ,1] != df.iloc[tmp_rx+1 ,1] :
                tmp_rx = tmp_rx + 1
            down_bound = tmp_rx+1
            # print(intent,verbal)
            intentId = self.getIntentId(intent)
            verbalId = self.getVerbalId(verbal)
            node = intentNode(intentId, verbalId, parent_node)
            if parent_node:
                # print("add Node")
                parent_node.addChild(node)

            if df.shape[1]>2 and df.iloc[up_bound][2] == df.iloc[up_bound][2]:
                self.buildTree(df.iloc[up_bound:down_bound,2:], node)
            self.root = node

    # def buildTree(self):
    #     logging.info("Bulding intent and verbal Tree ......")
    #     logging.info("Read content from xlsx......,(Path:{path})".format(path=self.xlsx))
    #     self.df = pd.read_excel(self.xlsx)
    #     logging.info("Split cell ......")
    #     self.split_cell()
    #     logging.info("Extract code ......")
    #     self.remove_redundant()
    #     logging.info("Add start intent ......")
    #     self.addStartCol()
    #     # pdb.set_trace()
    #     df = self.df
    #     count = 0
    #     # with open("huashu.txt","w") as f:
    #     #     for rx in range(df.shape[0]):
    #     #         path = []
    #     #         for lx in range(0, df.shape[1], 2):
    #     #             if df.iloc[rx][lx] != df.iloc[rx][lx]:
    #     #                 break
    #     #             else:
    #     #                 path.append("{intent}:{verbal}".format(intent=df.iloc[rx][lx],verbal = df.iloc[rx,lx+1]))
    #     #         f.write(",".join(path)+"\n")
    #
    #
    #     logging.info("Adding intent node to Graphy.......")
    #     for rx in range(df.shape[0]):
    #         count = count+1
    #         cur_node = self.root
    #         for lx in range(0,df.shape[1],2):
    #             if df.iloc[rx][lx] != df.iloc[rx][lx] :  #是否为空单元格
    #                 if df.iloc[rx][lx - 1] != df.iloc[rx][lx - 1]:
    #                     break
    #                 else:
    #                     intentId = self.getIntentId(end)
    #                     verbalId = self.getVerbalId(end)
    #             else:
    #                 intentId = self.getIntentId(df.iloc[rx][lx])
    #                 verbalId = self.getVerbalId(df.iloc[rx,lx+1])
    #
    #             assert verbalId2Abbre[verbalId] == verbalId2Abbre[verbalId]  #TTS代码必须存在
    #
    #             if not self.root:
    #                 self.root = intentNode(intentId, verbalId,None)
    #                 cur_node = self.root
    #
    #             if lx!=0:
    #                 pre_node = cur_node
    #                 cur_node = pre_node.addChild(intentNode(intentId,verbalId,pre_node))
    #
    #     logging.info("BUILD SUCCESSFULLY!")
    #     logging.info("verbal path count: " + str(count))
    #     logging.info("unique intent count: "+str(len(intentId2Abbre)))
    #     logging.info("unique verbal count: "+str(len(verbalId2Abbre)))
    #     self.intentId2Abbre = intentId2Abbre
    #     self.intentAbbr2Id = intentAbbr2Id
    #     self.verbalId2Abbre = verbalId2Abbre
    #     self.verbalAbbre2Id = verbalAbbre2Id

    def getIntentId(self,intent):
        if intent not in intentAbbr2Id.keys():
            intentId2Abbre.append(intent)
            intentAbbr2Id[intent] = len(intentId2Abbre)-1
        return intentAbbr2Id[intent]

    def getVerbalId(self,verbal):
        if verbal not in verbalAbbre2Id.keys():
            verbalId2Abbre.append(verbal)
            verbalAbbre2Id[verbal] = len(verbalId2Abbre) -1
        return verbalAbbre2Id[verbal]




    def addStartCol(self):
        df = self.df
        rowNum = df.shape[0]
        startCol = [start]*rowNum
        startDf = pd.DataFrame(data=[start], columns=["start"])
        oldDf = df
        newDf = pd.concat([startDf,oldDf],axis=1)
        self.df = newDf


    def split_prefix_cell(self):
        df = self.df
        count = 0
        total = 0
        for ci in range(df.shape[1] - 1, -1, -1):
            for ri in range(df.shape[0]):
                if df.iloc[ri, ci] != df.iloc[ri, ci]:
                    fake_sum = [1 for item in df.iloc[ri, :ci] if item == item]
                    #             print("here")
                    if len(fake_sum) <= 0:
                        count = count + 1
                        df.iloc[ri][ci] = df.iloc[ri - 1][ci]
                total = total + 1
        # print(count)
        # print(total)
        self.df = df


    def split_middle_cell(self):
        df = self.df
        count = 0
        total = 0
        for ci in range(df.shape[1] - 2, -1, -1):
            for ri in range(df.shape[0]):
                if df.iloc[ri, ci] != df.iloc[ri, ci] and df.iloc[ri, ci + 1] == df.iloc[ri, ci + 1]:
                    df.iloc[ri][ci] = df.iloc[ri - 1][ci]
                    count = count + 1
                total = total + 1
        # print(count)
        # print(total)
        self.df = df

    def split_backward_cell(self):
        count = 0
        total = 0
        df = self.df
        for ci in range(df.shape[1] - 1, -1, -2):
            for ri in range(df.shape[0]):
                if df.iloc[ri, ci] != df.iloc[ri, ci] and df.iloc[ri, ci - 1] == df.iloc[ri, ci - 1]:
                    df.iloc[ri][ci] = df.iloc[ri - 1][ci]
                    count = count + 1
                total = total + 1
        self.df = df

    def split_cell(self):
        self.split_prefix_cell()
        self.split_middle_cell()
        self.split_backward_cell()

    def remove_redundant(self):
        df = self.df
        for ci in range(df.shape[1] - 1, -1, -1):
            for ri in range(df.shape[0]):
                tmp = df.iloc[ri][ci]
                if tmp == tmp:
                    df.iloc[ri][ci] = re.findall(".*?([a-zA-Z\d]+)", df.iloc[ri][ci])[-1]

        self.df = df


def preVist(node,hs_path,record_list):
    huashu_path = hs_path[:]
    if node.getIntent() == end:
        return
    huashu_path.append(node.getVerbal())
    tmp_dict={}
    tmp_dict["huashu"] = "_".join(huashu_path)
    # if tmp_dict["huashu"] == "MK01_WFSB_MZ124_ND_SZ101_RS_SZ102_QSJ_SZ106":
    #     pdb.set_trace()
    #tree={item.getIntent():[item.getIntent()+"_2"] for item in node.clds if item.getIntent()!=end}
    tree={item.getIntent():[item.getIntent()+"_2"] for item in node.clds if item.getIntent()!=end and item.getIntent()!="WFSB"}
    if len(tree)<=0:
        return
    tmp_dict["tree"] = tree
    record_list.append(tmp_dict)
    if len(node.clds)<=0:
        return
    else:
        for item in node.clds:
            next_path = huashu_path[:]
            next_path.append(item.getIntent())
            preVist(item,next_path,record_list)










class intentNode:
    def __init__(self,intentId,verbalId,parent):
        self.intentId = intentId
        self.verbalId = verbalId
        self.clds = []
        self.parent = parent
        self.intentId2item= dict()
        self.cldsIntentIdSet = set()

    def addChild(self,child):
        if child.intentId not in self.cldsIntentIdSet:
            # print("addChild")
            self.clds.append(child)
            self.cldsIntentIdSet.add(child.intentId)
            self.intentId2item[child.intentId] = child
        return self.intentId2item[child.intentId]

    def showClds(self):
        logging.info(",".join([item.getIntent() for item in self.clds]))



    def getIntent(self):
        return intentId2Abbre[self.intentId]

    def getVerbal(self):
        return verbalId2Abbre[self.verbalId]

    def getPreVerbal(self):
        node = self
        verbal_list = []
        while node:
            verbal_list.append(node.getVerbal())
            verbal_list.append(node.getIntent())
            node = node.parent
        verbal_list.reverse()
        return verbal_list[1:]






def generate():
    return verbalTree()


#
def list2dict(record_list):
    tmp_dict={}
    huashu = "huashu"
    tree = "tree"
    all_intent_for_huashu = {}
    for item in record_list:
        tmp_huashu = item[huashu]
        tmp_tree = item[tree]

        last_huashu = tmp_huashu.split('_')[-1]
        last_tree = tmp_tree
        all_intent_for_last_huashu = all_intent_for_huashu.get(last_huashu, {})
        all_intent_for_last_huashu.update(last_tree)
        all_intent_for_huashu[last_huashu] = all_intent_for_last_huashu

        all_tree = tmp_dict.get(tmp_huashu,{})
        all_tree_keys = all_tree.keys()
        for k,v in tmp_tree.items():
            if k not in all_tree_keys:
                all_tree[k] = v
        tmp_dict[tmp_huashu] = all_tree
    result = [ {huashu:k,tree:v}for k,v in tmp_dict.items() ]
    result.extend([{huashu:k, tree:v} for k,v in all_intent_for_huashu.items()])
    return result






#read xlsx, and process
# df = pd.read_excel(u"../doc/intent.xlsx")
# df = split_cell(df)

# pdb.set_trace()


if __name__=="__main__":

    tree = verbalTree()
    # pdb.set_trace()
    record_list=[]
    preVist(tree.root,[],record_list)
    # pdb.set_trace()
    record_list = list2dict(record_list)

    f = open("record_path.json",'w')
    json.dump(record_list,f,indent=4)
