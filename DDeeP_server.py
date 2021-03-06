#server 코드

from PIL import Image
import argparse
from config import get_config
from mtcnn import MTCNN
from Learner import face_learner
from utils import load_facebank, prepare_facebank

import requests
from pathlib import Path
from multiprocessing import Process, Pipe,Value,Array

import os, sys, time
import numpy as np
import json,torch

from flask import Flask, render_template, jsonify, request
from mtcnn_pytorch.src.align_trans import get_reference_facial_points, warp_and_crop_face
from face_recognition import get_face_feature, get_max_cos #11.16


app = Flask(__name__)

server = "http://127.0.0.1:5000/"
#11.16
parser = argparse.ArgumentParser(description='for face verification')
parser.add_argument("-s", "--save", help="whether save",action="store_true")
parser.add_argument('-th','--threshold',help='threshold to decide identical faces',default=1.54, type=float)
parser.add_argument("-u", "--update", help="whether perform update the facebank",action="store_true")
parser.add_argument("-tta", "--tta", help="whether test time augmentation",action="store_true")
parser.add_argument("-c", "--score", help="whether show the confidence score",action="store_true")
args = parser.parse_args()
conf = get_config(False)

name_list=[]
register_list=[]
mtcnn=MTCNN()
print("mtcnn loaded")

learner = face_learner(conf, True)

learner.threshold = args.threshold

if conf.device.type == 'cpu':
    learner.load_state(conf, 'cpu_final.pth', True, True)
else:
    learner.load_state(conf, 'final.pth', True, True)
learner.model.eval()
print('learner loaded')

#register에서는 얼굴 촬영해서 얼굴의feature만 보내줌.
@app.route('/register',methods=["POST"])
def register():

    print("-------Register-------")

    register_face = request.json['face_list']

    register_np = np.array(register_face)
    if register_np.shape[0] > 1:
        return "no"
    elif register_np.shape[0] ==1:
        register_np = np.squeeze(register_np)
        register_pil = Image.fromarray(register_np, mode='RGB')
        feature = get_face_feature(conf, learner.model, register_pil)
        register_list.append(feature)

        register_name = request.json['register_name']
        name_list.append(register_name)


    return register_name+"register success!"

@app.route('/register_check',methods=["POST"])
def register_check():
    print(">>>>>>>Register_check<<<<<<<")

    face_list = request.json['face_list']
    check_list = []
    for idx in range(len(face_list)):
        face = np.array(face_list[idx])
        pil_img = Image.fromarray(face, mode='RGB')
        feature = get_face_feature(conf, learner.model, pil_img)
        i, cos_sim = get_max_cos(feature, register_list)
        if cos_sim > 0.97:
            check_list.append(name_list[i])
        else:
            check_list.append("unknown")
    print(check_list)
    check_list = {'check_list': check_list}

    return jsonify(check_list)

@app.route('/delete', methods=["DELETE"])
def delete():
    print("<<<<<<<Delete>>>>>>>")
    name = request.json['name']
    print(name)
    try:
        idx = name_list.index(name)
        del name_list[idx]
        del register_list[idx]
        return name + ' is deleted'
    except:
        return name + ' is not a registered face'


if __name__ =='__main__':
   app.run(host='0.0.0.0', port=5000,debug=True)
