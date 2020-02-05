from PIL import Image, ImageTk, ImageDraw
import cv2
from tkinter import Tk, Label, Button, Frame, Entry, messagebox
from src import detect_faces
import numpy as np
import requests

# 웹캠 함수
def show_frame():
    global face_list

    _, frame = cap.read()
    # frame = cv2.flip(frame, 1)
    cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    face_list = []
    bounding_boxes, landmarks = detect_faces(Image.fromarray(cv2image))

    if type(bounding_boxes) is not list:
        nrof_faces = bounding_boxes.shape[0]

        det = bounding_boxes[:, 0:4]
        bb = np.zeros((nrof_faces, 4), dtype=np.int32)

        for i in range(nrof_faces):
            bb[i][0] = det[i][0]
            bb[i][1] = det[i][1]
            bb[i][2] = det[i][2]
            bb[i][3] = det[i][3]

            if bb[i][0] <= 0 or bb[i][1] <= 0 or bb[i][2] >= len(cv2image[0]) or bb[i][3] >= len(cv2image):
                print('Face is very close! 0:', bb[i][0], '    1:', bb[i][1], '      2:', bb[i][2], '          3:', bb[i][3])
                continue

            cv2.rectangle(cv2image, (bb[i][0], bb[i][1]), (bb[i][2], bb[i][3]), (0, 255, 0), 3)
            sub_face = cv2image[bb[i][1]: bb[i][3], bb[i][0]: bb[i][2]]
            face_list.append(np.resize(np.array(sub_face).tolist(), (112, 112, 3)).tolist())
    #
    #     URL = server + "register_check"
    #     json_feed_verify = {'face_list': face_list}
    #     response = requests.post(URL, json=json_feed_verify)
    #     check_list = response.json()["check_list"]
    #
        # for idx in range(len(check_list)):
        #     if check_list[idx] == 'unknown':
        #         cv2image[bb[idx][1] : bb[idx][3], bb[idx][0] : bb[idx][2]] = cv2.GaussianBlur(cv2image[bb[idx][1] : bb[idx][3], bb[idx][0] : bb[idx][2]], (23, 23), 10)
            cv2image[bb[i][1]: bb[i][3], bb[i][0]: bb[i][2]] = cv2.GaussianBlur(cv2image[bb[i][1]: bb[i][3], bb[i][0]: bb[i][2]], (23, 23), 10)
            # else:
            #     cv2.putText(cv2image, check_list[idx], (bb[idx][0], bb[idx][1]), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3, cv2.LINE_AA)

        imgtk = ImageTk.PhotoImage(image=Image.fromarray(cv2image))
        lmain.imgtk = imgtk
        lmain.configure(image=imgtk)
        lmain.after(10, show_frame)

# 등록 버튼 이벤트 함수
def register_btn_click():
    register_name.focus()
    name = register_name.get()
    register_name.delete(0, len(register_name.get()))

    URL = server + "register"
    json_feed_verify = {'register_name': name, 'face_list': face_list}
    response = requests.post(URL, json=json_feed_verify)

def remove_btn_click():
    name = register_name.get()
    register_name.delete(0, len(register_name.get()))

    URL = server + "delete"
    json_feed_delete = {'name' : name}
    response = requests.delete(URL, json=json_feed_delete)



server = "http://104.196.231.8:5000/"

width, height = 800, 600
cap = cv2.VideoCapture("0")
cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

window = Tk()
window.title("title")
window.resizable(0, 0)
window.geometry("1500x800+20+20")

# 웹캠 구간
lmain = Label(window)
lmain.pack(side="left")

# 오른쪽 구간
sub_frame = Frame(window)
sub_frame.pack(side="left")

# 등록 버튼
register_btn = Button(sub_frame, text="Register", width=10, height=5, command=register_btn_click)
register_btn.grid(row=0, column=0, rowspan=3, columnspan=3, padx=5, pady=5)

# 레이블과 이름 입력 엔트리
register_label = Label(sub_frame, text="Input Name :")
register_label.grid(row=4, column=0, padx=5, pady=5)
register_name = Entry(sub_frame, width=10)
register_name.grid(row=4,column=1, padx=5, pady=5)

# 제거 버튼
remove_btn = Button(sub_frame, text="Remove", width=10, height=5, command=remove_btn_click)
remove_btn.grid(row=5, column=0, rowspan=3, columnspan=3, padx=5, pady=5)

show_frame()
window.mainloop()
