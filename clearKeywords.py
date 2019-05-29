from constants import MODEL_BACKUP_DIR
import commands, os, logging

def clearKeywords():
    keywordFile = commands.getoutput('find ' + MODEL_BACKUP_DIR + ' -name ' + 'keywords.txt')
    keywordFileList = keywordFile.split('\n')
    for keywordFile in keywordFileList:
        cmd = '> ' + keywordFile
        logging.info('cmd:{}'.format(cmd))
        os.system(cmd)

if __name__ == "__main__":
    clearKeywords()