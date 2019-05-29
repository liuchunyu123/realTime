import  os
import sys
sys.path.append("../")
NLU_IP = "http://114.67.85.13:8989"
DATA_RECEIVE_IP = "http://127.0.0.1"
DATA_RECEIVE_PORT = 8899
DATA_RECEIVE_URL = DATA_RECEIVE_IP+":"+str(DATA_RECEIVE_PORT)

SENTENCE_UPLOAD_URL = "/".join([NLU_IP,"text","uploader"])
HUSHU_UPLOAD_URL = "/".join([NLU_IP,"HejunHuaShu"])
RESET_URL = "/".join([NLU_IP,"ringOff"])



DATA_DIR = "/home/nnettest/work/hejun/PachiraAiModel/AiModel/data"
SUBDIR = "keyWordPhrases/{catName}Yes.txt"
MODEL_BACKUP_DIR = "/home/nnettest/work/hejun/PachiraAiModel/AiModel/model_backup"

SELECT_DATA_DIR = os.sep.join([DATA_DIR,"{catName}",SUBDIR])


RANDOM_SEED = None
pwd = os.getcwd()
HIST_DIR = os.path.join(os.path.abspath(os.path.dirname(pwd))+os.path.sep+"history")


EMULATOR = False


if not os.path.exists(HIST_DIR):
    os.makedirs(HIST_DIR)
