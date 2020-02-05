import cv2
from PIL import Image
import argparse
from pathlib import Path
from multiprocessing import Process, Pipe, Value, Array
import torch
from config import get_config
from mtcnn import MTCNN
from Learner import face_learner
from utils import load_facebank, draw_box_name, prepare_facebank
import requests
import os,sys,time
import numpy as np
from datetime import datetime

from mtcnn_pytorch.src.align_trans import get_reference_facial_points, warp_and_crop_face
#from face_verify_module import fn_face_verify
#from take_pic_module import get_pic


server = "http://104.196.231.8:5000/"

parser = argparse.ArgumentParser(description='take a picture')
parser.add_argument('--name', '-n', default='unknown', type=str, help='input the name of the recording person')
parser.add_argument('-th', '--threshold', help='threshold to decide identical faces', default=1.54, type=float)
parser.add_argument("-u", "--update", help="whether perform update the facebank", action="store_true")

args = parser.parse_args()

conf = get_config(False)

cap = cv2.VideoCapture(-1)
cap.set(3,1280)
cap.set(4,720)

mtcnn = MTCNN()
print('mtcnn loaded')
learner = face_learner(conf, True)
learner.threshold = args.threshold

if conf.device.type == 'cpu':
    learner.load_state(conf, 'cpu_final.pth', True, True)
else:
    learner.load_state(conf, 'final.pth', True, True)
learner.model.eval()
print('learner loaded')
"""
if args.update:
    targets, names = prepare_facebank(conf, learner.model, mtcnn, tta=args.tta)
    print('facebank updated')
else:
    targets, names = load_facebank(conf)
    print('facebank loaded')
"""


def DDeeP():
    isSuccess, frame = cap.read()

    if isSuccess:
        try:
            global name

            image = Image.fromarray(frame)
            bboxes, faces = mtcnn.align_multi(image, conf.face_limit, conf.min_face_size)
            bboxes = bboxes[:, :-1]  # shape:[10,4],only keep 10 highest possibiity faces
            bboxes = bboxes.astype(int)
            bboxes = bboxes + [-1, -1, 1, 1]  # personal choice
            face_list = []
            for idx, bbox in enumerate(bboxes):
                face_list.append(np.array(faces[idx]).tolist())

            URL = server + "register_check"
            json_feed_verify = {'face_list': face_list}
            response = requests.post(URL, json=json_feed_verify)
            check_list = response.json()["check_list"]
            for idx, bbox in enumerate(bboxes):
                if check_list[idx] == 'unknown':
                    frame[bbox[1] : bbox[3], bbox[0] : bbox[2]] = cv2.blur(frame[bbox[1] : bbox[3], bbox[0] : bbox[2]], (23,23))
                else:
                    frame = draw_box_name(bbox,"known", frame)

            cv2.imshow("My Capture", frame)
        except:
            print("detect error")

        if cv2.waitKey(1) & 0xFF == ord('t'):
            p = Image.fromarray(frame[..., ::-1])
            try:
                warped_face = np.array(mtcnn.align(p))[..., ::-1]
                re_img = mtcnn.align(p)
                tolist_face = np.array(re_img).tolist()
                #name 이부분에서 입력받도록 해야함.
                name = 'Seo Yeon'
                URL = server + "register"

                tolist_img = warped_face.tolist()
                json_feed = {'face_list': tolist_face,'register_name':name}
                response = requests.post(URL, json=json_feed)

            except:
                print('no face captured')



        if cv2.waitKey(0) & 0xFF == ord('c'):
            URL = server + "ReadFeature"
            params = {'name': name}
            res = requests.get(URL, params=params)
            res = res.json()
            res = res['result']
            print(res)
        # 키보드에서 n를 누르면 name update 이부분에 대해서는 추후에 업데이트 기능을 만들도록.
        if cv2.waitKey(0) & 0xFF == ord('n'):

            URL = server + 'update'
            new_name ='NEW'
            params = {'old_name': name, 'new_name': new_name}
            name = new_name
            res = requests.get(URL, params=params)
            print(res.text)


        # 키보드에서 u를 누르면 등록된 얼굴을 update할 수 있다.
        if cv2.waitKey(0) & 0xFF == ord('u'):
            newpic = Image.fromarray(frame[..., ::-1])
            new_img = np.array(newpic).tolist()
            URL = server + 'update'
            json_feed = {'name': name, 'new_image': new_img}
            res = requests.post(URL, json=json_feed)
        # 키보드에서 d를 누르면 삭제가능.
        if cv2.waitKey(0) & 0xFF == ord('d'):
            URL = server + 'delete'
            #이 부분을 변수화해야함.
            params = {'name': name}
            res = requests.delete(URL, params=params)
            print(res.text)


while cap.isOpened():
    DDeeP()
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break













