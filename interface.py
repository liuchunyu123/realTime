import sys
sys.path.append("../")
class textUploader:
    def __init__(self):
        self.callId = ""
        self.text = ""

    def getDict(self):
        d = dict()
        d["callId"] = self.callId
        d["text"] = self.text
        return d

class huaShu:
    def __init__(self):
        self.type = "normal"
        self.timestamp = ""
        self.text = ""
        self.callID = ""

    def getDict(self):
        d = dict()
        d["type"] = self.type
        d["timestamp"] = self.timestamp
        d["text"] = self.text
        d["callID"] = self.callID
        return d


class newTextUploader:
    def __init__(self):
        self.callId = ""
        self.text = ""


    def getDict(self):
        d = dict()
        d["callId"] = self.callId
        d["text"]