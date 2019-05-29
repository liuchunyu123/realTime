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
import regular_test

sentences = regular_test.get_sentence(file_path="../doc/output")
with codecs.open("../doc/output1",'w','utf-8') as f:
    for k,v in sentences.items():
        f.write(v[0])
        f.write('\t')
        f.write(k+"\n")

