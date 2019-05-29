import tornado.ioloop
import tornado.web
import json
import sys
sys.path.append("../")
from src import constants


current_intent=""
recog_result = ""
have_data = False

class uploadIntentHandler(tornado.web.RequestHandler):
    def post(self):
        data = json.loads(self.request.body)
        global current_intent,have_data,recog_result
        if data["intent_cat"]!="ASRWB":
            current_intent = data["intent_cat"]
            recog_result = data["text"]
            have_data = True
        ret = {"state":"SUCCESS"}
        self.write(json.dumps(ret))

class  haveDataHandler(tornado.web.RequestHandler):
    def get(self):
        if not have_data:
            self.write("")
        else:
            self.write("Yes")

class getIntentHandler(tornado.web.RequestHandler):
    def get(self):
        global current_intent, have_data,recog_result
        ret_intent = current_intent
        ret_text = recog_result
        current_intent = ""
        have_data = False
        self.write(ret_intent+"#"+ret_text)

class cleanIntentHandler(tornado.web.RequestHandler):
    def get(self):
        global current_intent, have_data,recog_result
        current_intent = ""
        have_data = False
        recog_result = ""

        self.write("Yes")




application = tornado.web.Application([
    (r"/uploadIntent", uploadIntentHandler),
    (r"/haveData",haveDataHandler),
    (r"/getIntent",getIntentHandler),
    (r"cleanIntent",cleanIntentHandler)

])

if __name__ == "__main__":
    application.listen(constants.DATA_RECEIVE_PORT,"0.0.0.0")
    tornado.ioloop.IOLoop.instance().start()
